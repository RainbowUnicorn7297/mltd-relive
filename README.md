# 偶像大師百萬人演唱會！劇場時光(重生版) | THE iDOLM@STER Million (RE)Live!: Theater Days

各位製作人大家好！我是彩虹獨角獸P～

MLTD的繁中服和韓服都在2022年1月28日正式停止營運。由於官方沒有提供轉移資料至日服的渠道，意味著大家花了不少時間和金錢收集回來的卡片、服裝和名牌在關服後也被永久刪除，也不能再以親切的中文和韓文介面來繼續培育偶像。本專案的目的是以運行本地伺服器的形式令海外版MLTD可以繼續遊玩，希望能給大家一點安慰，也不會讓官方的本地化翻譯白白浪費。

## 使用方法
1. [下載](https://github.com/RainbowUnicorn7297/mltd-relive/releases)並運行`mltd-relive-<程式版本>.exe`
2. 若果出現Windows防火牆提示，勾選全部選項並按允許存取（Allow access）

   <img width="392" alt="image" src="https://user-images.githubusercontent.com/67099591/152468770-f79c53e9-31a3-4a61-89c2-0fbbb4feced6.png">

3. 在手機上打開Wi-Fi設定，IP設定如下：

   - IP設定：靜態(Static)
   - IP位址(IP address)：手機的LAN IP
   - 閘道(Gateway)：路由器的閘道位址
   - 網路前置碼長度(Network prefix length)：一般家用LAN是24
   - DNS 1：電腦的LAN IP
   - DNS 2：可用路由器的DNS或公用DNS(如Google的8.8.8.8)

   <img width="200" alt="image" src="https://user-images.githubusercontent.com/67099591/152469590-782286c0-2a97-4326-8531-336524fa945c.png">

4. 運行遊戲

## 自行構建
1. 安裝[Python](https://www.python.org/downloads/)最新版本（目前是3.10.2）
2. 以系統管理員身份（Run as administrator）打開命令提示字元（cmd.exe），安裝以下所需套件：
```
pip install pyinstaller
pip install dnslib
pip install requests
pip install msgpack
pip install pycryptodome
```
3. 用GitHub Desktop複製或[手動下載](https://github.com/RainbowUnicorn7297/mltd-relive/archive/refs/heads/main.zip)程式碼至您的電腦上
4. 運行`prototype/build.bat`，會在`prototype/dist`資料夾裡生成`mltd-relive-prototype.exe`檔案

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

### 第二階段（預計2月16日前完成）
以本人帳號為藍本，在最短時間內讓劇情和演唱會，遊戲內最主要的兩個功能可以運作。

### 第三階段（預計6月中完成）
以一個通用帳號為基礎，已集齊全部卡片和服裝和解鎖所有劇情，將大部分社交類以外功能以最接近關服前的狀態呈現。活動和歌曲排名方面只有繁中服有備份，韓服則沒有。

### 第四階段（不定期更新）
到這裡可能會提供一些工具方便大家修改遊戲的數據和伺服器的行為，因為同一個通用帳號應該照顧不了所有的可能性。

## 討論區
開了一個簡單的Discord群組，歡迎大家加入和交流：https://discord.gg/EmeDpp8jSm
