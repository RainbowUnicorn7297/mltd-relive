from assets import asset

def application(environ, start_response):
##    print('\n'.join([str(('%s: %s' % (key, value)).encode('utf-8'))
##                     for key, value in environ.items()]))

    host = environ['HTTP_HOST']

##    if host == 'd3k5923sb1sy5k.cloudfront.net' or \
##       host == 'd1jbhqydw6nrn1.cloudfront.net':
    if host == 'rainbowunicorn7297.com':
        print('Serving asset...\n')
        status = '200 OK'
        headers = [('Content-Type', 'application/octet-stream'),
                   ('Cache-Control', 'public, no-transform, max-age=31536000, stale-if-error=31536000'),
                   ('max]
    
        start_response(status, headers)

        tokens = environ['PATH_INFO'].split('/')
        return [asset('zh' if host == 'd3k5923sb1sy5k.cloudfront.net' else 'ko',
                     tokens[-2], tokens[-1])]
    if host == 'theaterdays-zh.appspot.com' or \
       host == 'theaterdays-ko.appspot.com':
        status = '200 OK'
        headers = [('Content-Type', 'application/json'),
                   ('X-Encryption', 'on'),
                   ('X-Encryption-Compress', 'gzip'),
                   ('X-Encryption-Mode', '3')]

        start_response(status, headers)

        service = environ['PATH_INFO'].split('/')[-1]
        if service == 'GrecoService.AppBoot':
            return [b'1NzbIJMBO_44UDat84Ie6oj5Jzerxa3FmgLJTqKXhN-cFv85EFdXagBscxpZvtUGmu-0o5eOVi4XORUN-TvuiRPaB3oETdIO_giVfCmyfQs=']
        elif service == 'GameService.GetVersion':
            return [b'ECFgxyPGblwZo_xdafSu2O24jrHiJY9IJURP846gpKmbM2_wk4N5Kq9J3zra66aybkLKUmSEWHw8Dv0kaB-rzBALPwElXSWEJT01IpzUX0I4h63EAenFpl7ay8NTDTqP3EtCZS0dy-5DzeiYZ9SpXxgVtIH6W6rO6FP3mFL0kg6H-2syULm-tpEqzm3LGNyV6qWGQ8uSQM-mq0boc0vWEZSprkOTD46Zi-kEd_VDHUkr9wzA29U3RDw-ZlC_wPz1THdLLC-IehKwmuunvvaY-prlHTAe2JWstJNEWgKMLoZ9lgOPGVtybs45AGFNZlk0Xa_BnKR96ITcrWLy9j5qsdlrBwRFdkXlR4Lx4t-m5xonNnkE-jtDeggUqpSIq9xia3j2TtwAmF8_Ouxtj13cEDQJJ-upo27txdWQk_2rKyKD5bYCLB6SKL0MUSZzW0MD3NllssvoNG4wsghTIi-IAhMc0oZmkteTACJJ3y33zRCh6UC-CNeVm8OKVOt_M4-TDVORXhtNv_KTA2bd3yN2jmWGNimEfOpuNlyddUPC_fAgZx1uDsCpUSGA85f0TdeuwDB-JhA6zttbCzqC1wec4ovn9NUd9KUbDsVRaPwDgRo=']
        elif service == 'AuthService.Login':
            return [b'DItruvLu2vCce0NGUToZ6dE9FuhKg-bObpQE59d_Njc_qC_6VvbHxJ4oE-INzJ9RRE8KZthd39ZTeXE5YVcNJCzz7qElInB85l6Ye-qoIssbTHmiYv0c_rsNbM0KEaq4UNuyKJcqJQ4BhGiBYnx1Igld-p63CcEOfEH6xgsfCg0hrU7eD43iLy-eECUcrCzZzQdyYogrr5z0wxkkBVi0ZEMsAHI8t3xAr54PyTo0NJB_7pZ1UEEMlbnBK04dqiqw7B-tSzytBb5tmmwPzNvoo1hffdgI6kyusiPtUeJmkUbNwJcVQHEb4P2J9LIJBmnDqteT-V1ua4dnpLVrgimdTgUmbt63E9PKdHkfGzff6uCUbcFLjkq41QtHLfPKfyJURg48zVxjlBcMJfYH-NCydjjJ7Hs-0Ft5Y4XCg3B7s7MQT6yk0CrLz2NfPXJsqK2ZM39E7nbLQ6g_2ZIoXAkcPV7Yd3DRxLof2zwNdKnslAxJBEdIe-ky_URCAeqaMLNLi9hVdw__jn4CeJotrt2nSSZj79fVVEnLDOMTzlv7nftC5evhSjquLAItXNYr2g9IcFJBZWN1gULQQsdjFm_iQm_1ueoxA2tLfdX1ODPOy_i7BOkFSOZ_AmKVgZX-bEEuZuEKxa36xkcfXsXmTog_dRhPzEqqa0s4BrQMMSfOtq31-SZ7CGbwV3hIXa5ydNQub1JNYfUVQRT7yNKfiLoKyH47PuiCKEktXqMlt2H5zAV2CAQyXaBMeLRAesSTS-v4rqfcZH5WVe4lNhJ3KPoB6TGmmDSQkIi9konAXcmAiUgPXiPEBeQXxraN0CLSBPyTVlehyiOFZsk9HTzLMRqDWqyZnky3L2mTs3-9xxFBhZf9negGOoFwGTXcSjoKQDXqMqwqq6fhP3rnLb7PWePMEhfB791ZqwzBwaPsV8COU-_ZThfaMXlZnAEav9pcdrecvLITbfCuqx6_Xouyjt7jcBrUDZo-zUxO5mebFNAL7OnbZp_YPq9RqizXmjZOrmExbK31S_OqejcIYYwf630R7clafIFBm2OnvBN_sUY-7vD6r80EHndhVREkh-KQ8RHFKUNh63uTdL227NBs0uzUlRa4Qf4Q2KDf4OfGecGaSOqh36zcYsu1h3GCGxutHkf09g7whRG_noMvfP3NfY0RRkvs2YQ-RIT5GoaIwyha1pZ0grdrI_ZONBkEDyllafVhJuimwhu90gtnJEislkKseRC716xlaipbQCjLQmlqOoKbwMfiBBG5BTe9EyZbCI8lH1es7vDfeEqeKpYktYmG6T3oVTpttseBY9szGSTa463Bi4y91tyKVCvlstXzlaeYeGvdrCZGQgodnb6co7aXQ5AnJXgkehARKJEX2TrlQ-LwCU8Dxswmb3ddqRDrKcA0qf3xlEMACS_Fo-JqZXywbtkgy7ZFVubU9GYVAsYvd8mFOyGxPI0mb_FX66ybiYe8pp5JUDlme-REASGhYd7IitDDnv4ZOPfQjKKywal_OAYhLi1zJImm7r7QuqBAqoTwMrOCJiBton7HI4JlHoKfnATv4MsRR6AMT3ZSQtynmEPapqDutZI9RBhXDfEibQLxXzZGHcmAnpKyAolMYDmMVfLgyZheEnvb0IJrnQrP3_aEvfWuu3T2Vl7Lp0XQTdfV2W3SKdVPyRt3z-2rgP2Hak75mIJe2j4Vcd8qCgJy365JwQRSC9_3ZP6KvMccO7Bs27tSllKIebSqoxQUs_H4HNuD4GPdw_WO-dqHstXAWYUYWxj08TwQn0obiytI1h3Sn963tjqeFqxvCxkppTGE6RY1f3VV0GDyLGxkyOTLrfWarA4s6E7LPXGxqH57nzrrhAOO3qj3QNCE5hEE_SUVMJcz4b1ypvCstJAJ1v6-iggnjFOsKGK0-aQYIhPlqj2XbI8Bi4Jtw4uCN-UytHGDAHTXejzVb5iwPo2v4ygzKjRJTzVe6YMXHH-FCMwR4AZcXO6SE9EN2H_zlWzUd1Hm114cVhKeXNY_voLPfeMGcFYey-8PdR6V_CG_BB2SVxXaypdVPyRUcmh6smkm3Y4ParuJwDQ8QWgzNheIfBd9qFce2y0k_3mkzn1Ha44qQbb6W5PR6b3wRl_tcoyjNvbD-x3Vwv6tCVQAl8TRGzCM50BRTsdvnGTYHzNvCxR-XZADplvKr-28EiN8XZrKiYFgI1t64KCiO_Qif-Up3z0JSOWMfzaOxLiacXzUj8Aits-oH4zQ59u-PwY83oPjn4EZhrhmjEeRewFrHPWUHr5_Bo3AJ01ladws5wYP61Siq6OY5EoTfzFFQurqBR22lYyXuZ5wKBGBBM17cKxXacNXRUZml8PEjOg0jQJBYKNUaFFuyj4sYwUH9Ih36Zzzn8hp21AKpt1I2qxg_Z4yR6hV3gzPyqPfa17G_zkImeq0MZLEPZl1V5DVFqEVU5waRBYxMJZY0sTto1E2hGqC41wggH9uQqtkOWCrpx9cDO_WRhFdC_ogmjNYxkdGHSHdqbbDZAMoaxi7loYKZ7x1xQtv8nvDF8uhcpJs00KET19MXidyuLc7hXlyTdsXhNdE5eou90PmGIZwvI7b5fv1EiV-0S88Hk7bTZiOScZvd_IjsvNC7eGIwlIcnqmIwVgakkJTQr-X2ITLf9Z_at1fzDeUyLgQztmCps8MXc9lQyK_zjC_F0vKsNOIGdambI55xYtLyUnkoE8iJtN6VR7wZlz0zgZuIEMCa-fTeu1UFBOmy29u8AvMT4NVs6u7tLVSG6B2_QLtaSOytuQbQcxmGlhg6bZscvKiv0FGuam3L-CDMMRFHtIwFz9nRLYKHElccbWliqj9vI6WxZE7aEm7r--ubyyuCjyjcnPSJUBKAwnGuQTRHG-qIOI9IZUvd_-oGkY00QK8EP3hQ2-X5-Hz6dOZbemUQNvpuZfkBt-ujMBFERoPFxXapxALqZ424EpfEisrTrPqGXBqK_zJy2JXYoKXUepe_TMo2OMIpuwj71kJzcMI4KEZMFtLEExtHIcJ5LLIi2HNfxd-I3Y6HQJiEbyJ4XAJADFw8MuOyjTPQeDb1dAwa5D2Kr0ZIfcRTFpm_qisOqcK3oRUq8CW2yPzptB23vKgYFb4Nwp1oEzZc2ak_QgugXGWQN4RIISljNJmDMloepxbP-awoKNV7GceLtg7a6NM-srHiJybBN4n_5qVWF9UH_oava_9pC1pl7icSgrMx13nsnh8e3mbt0cgbSsyjvy7aTLrtNBNRnLzJjfSiAn68EUOUiQj0mM7FFKWrTDwVk8hNlBCOZEIcSZiyObFqgeOlw0E8Mui0PEGDjRdc9EAU3ukzM3iD_lsZORhvTC6Kr3ITfvHPHUNLA1BxPkHkb61IjlBgXFKLAEKhF1PXAnPMik_S1HQF9A9T1AXDG9rCEnLcHg_iH9cOf4hw2lDn9kx4ZeGRU_Ph6rS8iRYnvTYVpLRv9kRmnYt_c6lJvJ2ydyCRyZ-31pT2A945SrAbGqoKzzbRdNBhvukod8WPHpezUlwibnLQOZc6UVdFfNZFaz2aWN36LAlMWime62SSUBdh6OlYkBl0RO6xiUxZyUunMNey7QCDt9CKS6nhIeFEOSo2LuGxu57zbtcB3qUbokQ_zu_nfBUs9B4RU926XdM0Ho1xAULSUn_58AZGUBhyp7ECcKihd4gwxeLXoXfWHzqhDSZprowoQGfs_N64Chbz8L5pD5ne7p-jDSxZr6DQTqCPiKKUkpxUkheckq-e3zD3Cw5MUyunjnG41LLSrlqSUn44qCGdOLXwJsmuwCIZuwSwrbIPpeSc56qvgaAe0gNk0cHmxq3pPnC3dC5NpvY1bX_IiigLvto-xpL1L7xqQp6YMgPmM5nAoJPltZR2jGtpIMlpanbOSWAqrMkVEMIgAVM3fjNoK8D_8sOoauVFUSbGz-qesgdvnJt_qJqV0jAZAAy-pOgxPvP6w063y8AhypqbYsvJq61dWdItKQJBWtjJw8FDaY1ctilcD1Lu8j6ffFXDpBWwqTzfZjaspkW']
        elif service == 'AssetService.GetAssetVersion':
            return [b'jBFVrOjc7p7uFhNheHk7Ac9ArFHNJtLmwXn1Phx33AfLSLfB27Wl6XIwLUlJXn4AItEcvcY-JZO2M3dZHquhO3RvOZ1XzxzFtXYEeU8cEimUJQMJtOYDvdP6AgnL4KQJDV7HhkO6Ihyo8Ja7X8S-wdFVZwb4QO7nNrDnN71I8Z_UAnwAsYAlBtNzDVQlT5m9mT-m0NPcLqmwm8_BLpT-rsfyVMMGzumDxQ_HOwU6rP7zgpMQREXUrtexacq6hx116AJ_Un-hod4iLj2c-W9zWhmZ8tmiefvRn7OYbKf_qaOv2Y8YZD_6hpd8j9xpMbCo']
    else:
##        status = '503 Service Unavailable'
##        headers = [('Content-Type', 'text/html')]
##        
##        start_response(status, headers)
##
##        return [b'']
        start_response('200 OK', [('Content-Type', 'text/html')])
        return [b'NYjAxekgNSQksb1oMl6lRnq3VxwOrYJvr-nPVAwXEDw.-f-Bwstx_Q_vx2FH2p9apC9gSQXg6l5tbAuGI04DQcg']
