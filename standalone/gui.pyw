import os
import traceback
from multiprocessing import Pipe, Process, freeze_support, set_start_method
from tkinter import *
from tkinter import messagebox, ttk

from mltd.models.setup import (check_database_version, cleanup, setup,
                               upgrade_database)
from mltd.servers import api_server, dns, proxy
from mltd.servers.config import api_port, config, server_language, version
from mltd.servers.dns import dns_port, get_lan_ips
from mltd.servers.logging import handler, logger
from mltd.servers.proxy import proxy_port


class CustomProcess(Process):

    def __init__(self, *args, **kwargs):
        Process.__init__(self, *args, **kwargs)
        self.parent_conn, self.child_conn = Pipe()
        self._exception = None

    def run(self):
        try:
            Process.run(self)
            self.child_conn.send(None)
        except Exception:
            self.child_conn.send(traceback.format_exc())

    @property
    def exception(self):
        if self.parent_conn.poll():
            self._exception = self.parent_conn.recv()
        return self._exception


class MLTDReliveGUI:

    def __init__(self):
        self.root = Tk()
        self.root.title(f'mltd-relive Standalone v{version}')
        self.root.resizable(False, False)

        style = ttk.Style()
        style.configure('Green.TButton', foreground='green')
        style.map('Green.TButton', foreground=[('disabled', 'grey'),
                                               ('active','green')])
        style.configure('Red.TButton', foreground='red')
        style.map('Red.TButton', foreground=[('disabled', 'grey'),
                                             ('active','red')])

        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.grid()

        status_frame = ttk.Frame(main_frame, padding=10)
        status_frame.grid(column=0, row=0)
        self.server_status = 'Stopped'
        self.status_label = ttk.Label(
            status_frame, text=f'Server Status: {self.server_status}',
            font=(None, 14), foreground='red', width=20, anchor=CENTER)
        self.status_label.grid(column=0, row=0)
        self.progress_bar = ttk.Progressbar(status_frame, mode='indeterminate')

        button_frame = ttk.Frame(main_frame, padding=10)
        button_frame.grid(column=1, row=0)
        self.start_server_button = ttk.Button(
            button_frame, text='Start Server', command=self.start_server,
            style='Green.TButton', width=20
        )
        self.start_server_button.grid(column=1, row=0)
        self.stop_server_button = ttk.Button(
            button_frame, text='Stop Server', command=self.stop_server,
            style='Red.TButton', width=20
        )
        self.reset_button = ttk.Button(
            button_frame, text='Reset Data', command=self.reset_data,
            width=20
        )
        self.reset_button.grid(column=1, row=1)

        info_frame = ttk.Labelframe(main_frame, text='Server Info', padding=10)
        info_frame.grid(column=0, row=2, sticky=(N, S, W, E))
        lan_ipv4, lan_ipv6 = get_lan_ips()
        if not lan_ipv4:
            lan_ipv4 = 'N/A'
        if not lan_ipv6:
            lan_ipv6 = 'N/A'
        ttk.Label(info_frame, text=f'IPv4: {lan_ipv4}').grid(
            column=0, row=0, padx=5, sticky=W)
        ttk.Label(info_frame, text=f'IPv6: {lan_ipv6}').grid(
            column=0, row=1, padx=5, sticky=W)
        ttk.Label(info_frame, text=f'DNS Port: {dns_port}').grid(
            column=1, row=0, padx=5, sticky=W)
        ttk.Label(info_frame, text=f'Proxy Port: {proxy_port}').grid(
            column=1, row=1, padx=5, sticky=W)
        ttk.Label(info_frame, text=f'API Port: {api_port}').grid(
            column=1, row=2, padx=5, sticky=W)

        options_frame = ttk.Labelframe(main_frame, text='Options', padding=10)
        options_frame.grid(column=1, row=2, sticky=(N, S, W, E))
        ttk.Label(options_frame, text='Game Client Language:').grid(
            column=0, row=0, rowspan=2, sticky=E)
        self.language = StringVar()
        self.language.set(config['default']['language'])
        self.zh_radio_button = ttk.Radiobutton(
            options_frame, text='繁體中文', variable=self.language, value='zh',
            command=self.change_language
        )
        self.zh_radio_button.grid(
            column=1, row=0, sticky=W)
        self.ko_radio_button = ttk.Radiobutton(
            options_frame, text='한국어', variable=self.language, value='ko',
            command=self.change_language
        )
        self.ko_radio_button.grid(
            column=1, row=1, sticky=W)

    def update_server_status(self):
        if (self.api_process.is_alive()
                or self.proxy_process.is_alive()
                or self.dns_process.is_alive()):
            if self.api_process.exception:
                logger.error(self.api_process.exception)
                messagebox.showerror('Error', self.api_process.exception)
            elif self.proxy_process.exception:
                logger.error(self.proxy_process.exception)
                messagebox.showerror('Error', self.proxy_process.exception)
            elif self.dns_process.exception:
                logger.error(self.dns_process.exception)
                messagebox.showerror('Error', self.dns_process.exception)
            if self.server_status == 'Starting':
                self.server_status = 'Started'
                self.status_label.config(
                    text=f'Server Status: {self.server_status}',
                    foreground='green')
                self.start_server_button.grid_forget()
                self.stop_server_button.grid(column=1, row=0)
                self.stop_server_button.configure(state=NORMAL)
                self.progress_bar.stop()
                self.progress_bar.grid_forget()
                logger.info(f'Server started.')
            self.root.after(200, self.update_server_status)
            return
        self.api_process.join()
        self.proxy_process.join()
        self.dns_process.join()
        if self.server_status == 'Stopping':
            self.server_status = 'Stopped'
            self.status_label.config(
                text=f'Server Status: {self.server_status}',
                foreground='red')
            self.start_server_button.grid(column=1, row=0)
            self.stop_server_button.grid_forget()
            self.start_server_button.configure(state=NORMAL)
            self.reset_button.config(state=NORMAL)
            self.zh_radio_button.config(state=NORMAL)
            self.ko_radio_button.config(state=NORMAL)
            logger.info(f'Server stopped.')

    def start_server(self):
        self.server_status = 'Starting'
        if not os.path.isfile('mltd-relive.db'):
            self.reset_data()
            return
        upgrade_database()

        handler.doRollover()
        self.status_label.config(text='Starting Server...',
                                 foreground='black')
        logger.info(f'Starting server...')
        self.start_server_button.config(state=DISABLED)
        self.reset_button.config(state=DISABLED)
        self.zh_radio_button.config(state=DISABLED)
        self.ko_radio_button.config(state=DISABLED)
        self.progress_bar.grid(column=0, row=1, sticky=(W, E))
        self.progress_bar.start()
        self.proxy_process = CustomProcess(target=proxy.start, daemon=True)
        self.proxy_process.start()
        self.api_process = CustomProcess(target=api_server.start, daemon=True)
        self.api_process.start()
        self.dns_process = CustomProcess(target=dns.start, daemon=True)
        self.dns_process.start()
        self.root.after(13400, self.update_server_status)

    def stop_server(self):
        self.server_status = 'Stopping'
        self.status_label.config(text='Stopping Server...',
                                 foreground='black')
        logger.info(f'Stopping server...')
        self.start_server_button.config(state=DISABLED)
        self.proxy_process.terminate()
        self.api_process.terminate()
        self.dns_process.terminate()
        self.root.after(200, self.update_server_status)

    def update_reset_data_progress(self):
        if self.process.is_alive():
            if self.process.exception:
                logger.error(self.process.exception)
                messagebox.showerror('Error', self.process.exception)
            self.root.after(200, self.update_reset_data_progress)
            return
        self.process.join()
        if self.server_status == 'Starting':
            self.start_server()
            return
        self.status_label.config(
            text=f'Server Status: {self.server_status}', foreground='red')
        self.start_server_button.config(state=NORMAL)
        self.reset_button.config(state=NORMAL)
        self.zh_radio_button.config(state=NORMAL)
        self.ko_radio_button.config(state=NORMAL)
        self.progress_bar.stop()
        self.progress_bar.grid_forget()

    def reset_data(self):
        if os.path.isfile('mltd-relive.db'):
            check_database_version()
            if not messagebox.askyesno(
                    title='Warning',
                    message='Database already exists. Reset all data?'):
                return
            cleanup()
            logger.info('Dropped all tables.')

        handler.doRollover()
        self.status_label.config(text='Initializing Data...',
                                 foreground='black')
        self.start_server_button.config(state=DISABLED)
        self.reset_button.config(state=DISABLED)
        self.zh_radio_button.config(state=DISABLED)
        self.ko_radio_button.config(state=DISABLED)
        self.progress_bar.grid(column=0, row=1, sticky=(W, E))
        self.progress_bar.start()
        self.process = CustomProcess(target=setup)
        self.process.start()
        self.root.after(200, self.update_reset_data_progress)

    def change_language(self):
        global server_language
        language = self.language.get()
        config.set_config('language', language)
        server_language = language
        logger.info(f'Changed language to {language}.')


def report_callback_exception(self, exc, val, tb):
    logger.error(traceback.format_exc())
    messagebox.showerror('Error', message=traceback.format_exc())


if __name__ == '__main__':
    freeze_support()
    set_start_method('spawn')

    Tk.report_callback_exception = report_callback_exception

    gui = MLTDReliveGUI()
    if os.path.isfile('mltd-relive.db'):
        gui.root.after_idle(gui.start_server)
    gui.root.mainloop()

