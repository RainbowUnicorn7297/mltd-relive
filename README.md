# 偶像大師百萬人演唱會！劇場時光(重生版) | THE iDOLM@STER Million (RE)Live!: Theater Days

各位製作人大家好！我是彩虹獨角獸P～

MLTD的繁中服和韓服都在2022年1月28日正式停止營運。由於官方沒有提供轉移資料至日服的渠道，意味著大家花了不少時間和金錢收集回來的卡片、服裝和名牌在關服後也被永久刪除，也不能再以親切的中文和韓文介面來繼續培育偶像。本專案的目的是以運行本地伺服器的形式令海外版MLTD可以繼續遊玩，希望能給大家一點安慰，也不會讓官方的本地化翻譯白白浪費。

## 版本說明
### Prototype版（最新版本：[prototype-v1.0.2](https://github.com/RainbowUnicorn7297/mltd-relive/releases/tag/prototype-v1.0.2)）
以本人帳號為基礎的版本，功能上比較局限，主要支援劇情（含mail及部落格）及演唱會（含自訂團體卡片及服裝）。具有以下特性：
- 只支援繁中版。
- 以靜態方式為主回應API請求。絕大部分數值不會在遊戲過程中改變，重啟遊戲後會重置所有遊戲內容。
- 演唱會可自訂團體卡片及服裝，但團體狀態在完成歌曲後不會被保留。
- mail和部落格會按預設排序一次過顯示全部內容，不支援自訂篩選及排序。
- 未回信的mail不能以回信來解鎖新mail。
- 未解鎖的覺醒故事不能透過進行覺醒來解鎖。

### Standalone版（最新版本：[standalone-v0.0.4](https://github.com/RainbowUnicorn7297/mltd-relive/releases/tag/standalone-v0.0.4)）
以一個已解鎖全部內容的通用帳號為基礎的版本，目標於v1.0.0將絕大部分功能以最接近關服前的狀態呈現。具有以下特性：
- 支援繁中版及韓版。
- 遊玩過程中的數據會儲存在本地資料庫中。首次啟動本地伺服器時，會在程式的同一個資料夾內建立資料庫檔案。
- 活動及歌曲排名只有繁中服有關服前的記錄（Blooming Star和THE IDOLM@STER 初星-mix的歌曲排名除外），韓服則沒有記錄。
- `mltd-relive.db`是SQLite資料庫，可以用[DB Browser for SQLite](https://sqlitebrowser.org)等工具修改遊戲數值。

以下是目前版本支援的主要功能：
- 使用密碼繼承通用帳號
- 登入
   - 登入獎勵
   - 偶像、事務員及製作人生日對話
   - 特別節日對話
- 任務
   - 每日任務
   - 每週任務
- 偶像
   - 編制團體
- 演唱會全部功能

## 使用方法
### 注意事項
- 首次啟動程式時，會在程式的同一個資料夾內建立資料庫、設定檔及記錄檔。啟動前請預留約100MB的空間。
- 由於伺服器必須使用連接埠53和443，Ubuntu版需要以root權限運行。
- 程式使用以下作業系統構建：
   - Windows Server 2022
   - Ubuntu 22.04
   - macOS 12 Monterey

  Windows版於Windows 11亦測試過可以正常運行。其他作業系統版本若不能運行的話，可以[自行構建](#自行構建)。

### 步驟
1. [下載](https://github.com/RainbowUnicorn7297/mltd-relive/releases)並運行程式
   > Ubuntu版需要以root權限運行，例如`sudo ./mltd-relive-standalone-v1.0.0-ubuntu`
2. 選擇遊戲語言（繁體中文或韓文），然後按＂Start Server＂

   <img width="392" alt="image" src="https://user-images.githubusercontent.com/67099591/261151800-e8103b40-387e-46c6-8437-0f9ea65b202a.png">

3. 等待程式建立資料庫和啟動伺服器，直至出現＂Server Status: Started＂

   <img width="392" alt="image" src="https://user-images.githubusercontent.com/67099591/261154195-4420e0ea-b8af-48ce-abd9-2b8d46af8aaf.png">

   > Windows版若果出現Windows防火牆提示，勾選全部選項並按允許存取（Allow access）
   > <img width="392" alt="image" src="https://user-images.githubusercontent.com/67099591/152468770-f79c53e9-31a3-4a61-89c2-0fbbb4feced6.png">

4. 將手機的DNS設定成程式上顯示的IPv4或IPv6
   > 這裡以Android手機作為例子，iOS基本上也是同樣原理
   <table>
   <thead>
   <tr>
   <th width="500px">方法1（推薦）</th>
   <th width="500px">方法2</th>
   </tr>
   </thead>
   <tbody>
   <tr>
   <td>

   下載[DNSChanger for IPv4/IPv6](https://play.google.com/store/apps/details?id=com.frostnerd.dnschanger)，輸入以下設定：
   - Primary server: 電腦的LAN IP（程式上顯示的IPv4）

   最後按＂START＂

   <img width="200" alt="image" src="https://github.com/RainbowUnicorn7297/mltd-relive/assets/67099591/01b36c40-b114-4b6f-8a80-237970115fd5">

   </td>
   <td>
   在手機上打開Wi-Fi設定，IP設定如下：

   - IP設定：靜態（Static）
   - IP位址（IP address）：手機的LAN IP
   - 閘道（Gateway）：路由器的閘道位址
   - 網路前置碼長度（Network prefix length）：一般家用LAN是24
   - DNS 1：電腦的LAN IP（程式上顯示的IPv4）

   最後關掉再打開手機Wi-Fi

   <img width="200" alt="image" src="https://github.com/RainbowUnicorn7297/mltd-relive/assets/67099591/6b11959a-c1ee-4bfc-8677-fbaf244dfb26">
   </td>
   </tr>
   </tbody>
   </table>

5. 運行遊戲
   > 原始APK在Android 12L或以上不能運行，可下載[繁中版](https://mega.nz/file/HMgiTSbI#cy7z52H6zBOSdSX5Xok1GKQ4yT7k6K1ctjV6Heceu3I)或[韓版](https://mega.nz/file/2dBgiBQY#NBgo-1rTW7g1Jtm9FLYZ61KoOP4HFoElxO75dzMyXew)經修正後的APK。
6. 首次進入遊戲時會出現以下提示，按＂繼承資料＂

   <img width="520" alt="image" src="https://user-images.githubusercontent.com/67099591/208608928-05a71f22-69a2-4ffc-b8d6-3451e06e77e8.png">

7. 按＂使用密碼繼承＂，再按＂OK＂

   <img width="520" alt="image" src="https://user-images.githubusercontent.com/67099591/208609764-a79d551b-fdf4-4da8-8a46-c6bad6e884f2.png">

8. 隨意輸入長度為8個字元的密碼，最後按＂決定＂

   <img width="520" alt="image" src="https://user-images.githubusercontent.com/67099591/208610514-01adc780-a92e-4f50-b459-e51361d7af49.png">

## 自行構建
1. 安裝[Python](https://www.python.org/downloads/)最新版本（目前是3.11.4）
2. 用GitHub Desktop複製或[手動下載](https://github.com/RainbowUnicorn7297/mltd-relive/archive/refs/heads/main.zip)程式碼至您的電腦上
3. 打開CLI（例如Windows的cmd.exe或Linux/macOS的Terminal），移至程式碼的資料夾（`cd mltd-relive`），然後輸入以下指令：
   - Windows
   ```
   python -m venv env
   .\env\Scripts\activate
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   cd standalone
   ..\env\Scripts\pyinstaller gui_windows.spec
   ```
   - Unix/Linux
   ```
   python -m venv env
   source env/bin/activate
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   cd standalone
   ../env/bin/pyinstaller gui_ubuntu.spec
   ```
   - macOS
   ```
   python -m venv env
   source env/bin/activate
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   cd standalone
   ../env/bin/pyinstaller gui_macos.spec
   ```
4. 以上指令會在`standalone/dist`資料夾裡生成程式檔
   - Windows: `mltd-relive-standalone.exe`
   - Unix/Linux: `mltd-relive-standalone`
   - macOS: `mltd-relive-standalone.app`資料夾

## 計劃

### 第一階段（已完成）
首要任務是找出最簡單的方法令遊戲把所有HTTPS請求（包括API，資源和網頁）重新定向至本地伺服器，以及探索將HTTPS請求變為HTTP或使用自簽憑證也不會出錯的可能性，盡可能在Android手機沒ROOT權限和沒修改遊戲apk來進行。這樣的話理論上iOS也可以用，也就能惠及更多製作人。

重新定向的問題比較容易解決，設置一個DNS伺服器或代理，再將運行遊戲的裝置上的Wi-Fi設定改DNS就可以了。

把HTTPS請求改成HTTP基本上不可行，因為首先建立連線的一方是遊戲那邊，一開始就決定了所有請求必須用HTTPS。

自簽憑證方面，API可以，但網頁和資源不行。沒網頁的影響就是公告，轉蛋詳情和繼承資料時的注意事項不能顯示，相對輕微。沒資源的話，遊戲就當然不能玩了。目前想到的解決辦法有以下幾種：
1. 在Android手機的User credentials安裝自簽憑證，然後重新打包遊戲apk去信任用戶自簽憑證。這個方法設置工序比較複雜，不支援iOS，而且Android新版本的保安規格會越收越緊，不保證以後仍可行。
2. 使用由憑證頒發機構(CA)簽發的憑證。由於資源伺服器的URL是由API提供，在測試過程中發現把URL指向其他域名（如[https://rainbowunicorn7297.com](https://rainbowunicorn7297.com)），遊戲會從這個新域名下載資源。購買域名後，可用[Let's Encrypt](https://letsencrypt.org)等服務免費取得CA簽發憑證和密鑰（有效期最多90天），或購買CA簽發憑證和密鑰（有效期可長達5年或以上，但據聞最新簽發的憑證有效期超過398天的話，客戶端可能會出現警告或錯誤）。這個方法的缺點是有效期過後，要重新簽發一組新的憑證和密鑰，然後大家需要去下載才能繼續玩。
3. 跟官方一樣設立一個Amazon CloudFront CDN或其他CDN作資源伺服器。免費的CDN一般最多給每個月1TB流量，遊戲資源各平台（繁中服和韓服、Android和iOS）總共約37.5GB，每次播放劇情都要從伺服器下載資源，不確定流量是否足以應付。收費的話，價錢看起來相當不便宜。
4. 在免費CDN前面再加Cloudflare來幫助分流。這個方法參考了[這篇文章](https://advancedweb.hu/how-to-use-a-custom-domain-on-cloudfront-with-cloudflare-managed-dns/)，看起來是相當不錯的方法，只要Cache-Control等控制快取的參數設定得宜的話，理論上是可以處理大量流量的。

目前會以第四個方法來繼續測試和開發，維持域名和Amazon S3儲存資源，成本每年大約US$20，然後未來會提供第二個方法給大家作後備方案。如果大家有更好的方法請賜教，可以在Discord或者直接在GitHub開Issue跟我說。

2022年6月9日更新：Cloudflare最近推出了[R2](https://blog.cloudflare.com/r2-open-beta/)，收費模式跟其他雲端服務截然不同，不向流量收費。目前已經把資源放到這裡，以後再也不用擔心流量的問題了。

### 第二階段（已完成）
以本人帳號為藍本，在最短時間內讓劇情和演唱會，遊戲內最主要的兩個功能可以運作。

### 第三階段（預計2024年5月完成）
以一個通用帳號為基礎，已集齊全部卡片和服裝和解鎖所有劇情，將大部分社交類以外功能以最接近關服前的狀態呈現。活動和歌曲排名方面只有繁中服有備份，韓服則沒有。

### 第四階段（不定期更新）
到這裡可能會提供一些工具方便大家修改遊戲的數據和伺服器的行為，因為同一個通用帳號應該照顧不了所有的可能性。

## 討論區
開了一個簡單的Discord群組，歡迎大家加入和交流：https://discord.gg/EmeDpp8jSm
