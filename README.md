# Appium OCR プラグイン

これは[Tesseract](https://github.com/tesseract-ocr/tesseract)ベースのAppium用OCRプラグインです。[Tesseract.js](https://tesseract.projectnaptha.com/) のOCR処理に依存します.

## 機能

1. **New OCR endpoint** - call a new Appium server endpoint to perform OCR on the current screenshot, and return matching text and metadata.
2. **OCR context** - switch to the `OCR` context and the page source will be updated to respond with XML corresponding to text objects found on the screen.
3. **Find elements by OCR text** - When in the OCR context, using XPath will find "elements" based on the OCR XML version of the page source. These found elements can then be interacted with in minimal ways (click, getText) based purely on screen position.

## 事前準備

* Appium Server 2.0+
Appium 2.0 のインストール方法： `npm install -g appium@next`
https://www.headspin.io/blog/installing-appium-2-0-and-the-driver-and-plugins-cli

* Node v16.1 推奨（Node v18を使用すると、Teserractがランタイムエラーで異常終了します）

## インストレーション - サーバー側

CLIから本プラグインをAppiumへインストールする:

```
appium plugin install --source=npm appium-ocr-plugin
```

## インストレーション - クライアント側

クライアント側へ手動で追加しなければいけないメソッドは、getOcrText用のエンドポイントのみです。この機能に対する公式のクライアントプラグインは今のところありません。将来的には開発されるかもしれません。しかし、参考までに、WebdriverIOにコマンドを追加する方法は以下のとおりです。

```js
browser.addCommand('getOcrText', command('POST', '/session/:sessionId/appium/ocr', {
    command: 'getOcrText',
    description: 'Get all OCR text',
    ref: '',
    variables: [],
    parameters: []
}))
```

```python
class CustomURLCommand(ExtensionBase):
    def method_name(self):
        return 'get_ocr_text'

    def get_ocr_text(self, argument):
        return self.execute(argument)['value']

    def add_command(self):
        return ('post', '/session/$sessionId/appium/ocr')
```

## 有効化

プラグインは、Appiumサーバーの起動時にONにしないとアクティブになりません。

```
appium --use-plugins=images
```

## 使用方法

### 応答値に関する用語

このプラグインがリターンする応答値の意味は以下のとおりです。

* `confidence` - 該当するテキストに対するOCR処理の結果に対するTesseractの信頼度(0～100のスケール)
* `bbox` - "bounding box"は、`x0`, `x1`, `y0`, `y1`を含むオブジェクトです。 `x0` は検出されたテキストの外枠を囲うボックスの左側のx座標を意味し、`x1`は右側のx座標を意味します。`y0`はy座標の下側、`y1`はy座標の上側を意味します。

### `getOcrText` エンドポイント

POSTリクエストを `/session/:sessionid/appium/ocr` に送ると、現在のスクリーンショットに対してOCRが実行され、3つのキーを含むJSONオブジェクトで応答します。

* `words` - Tesseractが推測する個別の単語
* `lines` - Tesseractが推測するテキスト文章
* `blocks` - Tesseractが推測する連続したテキストブロック

これらのキーはそれぞれ、3つのキーを含むOCRオブジェクトの配列を参照します。

* `text`: 発見されたテキスト
* `confidence`: 検出されたテキストに対する信頼度
* `bbox`: 検出されたテキストブロックの境界線（上記参照）

### `OCR` コンテキスト

このプラグインを有効にすると、`getContexts` を呼び出したときに、`OCR` という追加のコンテキストが利用できるようになります。OCR` コンテキストに切り替えると (`driver.setContext('OCR')` または同等の方法で)、特定のコマンドに新しい動作が追加されます。
#### ページソースの入手

OCRコンテキストでページソースを取得する場合、基本、取得結果は `getOcrText` コマンドが返すものと同じ情報を持つXMLドキュメントになります。以下はその例です。

```xml
<?xml version="1.0" encoding="utf-8"?>
<OCR>
    <words>
        <item confidence="82.16880798339844" x0="196" x1="237" y0="528" y1="542">photo</item>
        <item confidence="87.81583404541016" x0="243" x1="288" y0="527" y1="542">library</item>
        <item confidence="92.86579132080078" x0="21" x1="69" y0="567" y1="581">Picker</item>
    </words>
    <lines>
        <item confidence="87.97928619384766" x0="34" x1="66" y0="18" y1="30">9:38</item>
        <item confidence="64.12049865722656" x0="312" x1="355" y0="18" y1="29">T -</item>
        <item confidence="88.1034164428711" x0="154" x1="221" y0="59" y1="75">The App</item>
        <item confidence="92.1086654663086" x0="9" x1="179" y0="99" y1="110">Choose An Awesome View</item>
        <item confidence="92.64363098144531" x0="21" x1="93" y0="136" y1="149">Echo Box</item>
        <item confidence="89.5836410522461" x0="21" x1="327" y0="157" y1="172">Write something and save to local memory</item>
    </lines>
    <blocks>
        <item confidence="87.97928619384766" x0="34" x1="66" y0="18" y1="30">9:38</item>
        <item confidence="64.12049865722656" x0="312" x1="355" y0="18" y1="29">T -</item>
        <item confidence="88.1034164428711" x0="154" x1="221" y0="59" y1="75">The App</item>
        <item confidence="92.1086654663086" x0="9" x1="179" y0="99" y1="110">Choose An Awesome View</item>
        <item confidence="92.64363098144531" x0="21" x1="93" y0="136" y1="149">Echo Box</item>
        <item confidence="89.5836410522461" x0="21" x1="327" y0="157" y1="172">Write something and save to local memory</item>
    </blocks>
</OCR>
```

### エレメントの検出

OCR コンテキストでは、`xpath` ロケーターを使用してXML内のエレメンを参照します。前述にある通り、セレクターの値にはページソース内のエレメントをクエリーする記述を設定します。一致する要素が見つかれば、該当エレメントがクライアントに返されます。これらの要素は、標準的なUI要素（つまり、 `XCUIElementTypeText` や `android.widget.TextView` ）ではなく、以下にあげる限定されたメソッドのみをサポートします。

* `Click Element`: 選択した要素のバウンディングボックスの中心点をシングルタップするアクションを実行します。
* `Is Element Displayed`: 原則、常に `true` を返します。表示されていなければ、OCRとして検出されません。
* `Get Element Size`: ボックスの高さと幅を返します。
* `Get Element Location`: `x0` と `y0` が指すポイントを返します。
* `Get Element Rect`: `x0`, `x1`, `y0`, `y1`の各数値を返します。
* `Get Element Text`: OCRで検出されたテキスト（ページソース出力と同じテキスト）を返します。
* `Get Element Attribute`: 属性の値を返します。現在、attribute (`confidence`) のみがサポートされます。

Clickコマンドを使って一例を示します。まずOCR コンテキストへ移行してください。ページソースが上記の例と一致するのであれば、以下Javascriptの例となりますが、以下に従ってエレメントをクリックできます (WebdriverIOに従って、お使いのクライアントライブラリで動作するように変換してください)。

```js
const element = await driver.$('//lines/item[text() = "Echo Box"]')
await element.click()
```
```Python
element = driver.find_element(by=By.XPATH, value="//lines/item[contains(text(), 'Login Screen')]")
element.click()
```

上記コマンドは、Tesseractが "Echo Box"のテキストラインがあると判断した画面領域の中心をクリックするものです。

### 設定

場合によっては、プラグインの動作にいろいろと手を加えることが必要になることがあります。その際に利用できるのが下の設定です。Capabilityとして設定するか（例：`appium:settings[<settingName>] = <settingValue>` ）、もしくは、クライアントライブラリの設定更新機能（例：`driver.updateSettings(...)` ）として設定できます。

|Setting name|Description|Default|
|------------|-----------|-------|
|`ocrShotToScreenRatio`|(Number) プラットフォームから返されるスクリーンショットの寸法は、プラットフォームが使用する画面座標と異なる場合があります。この場合、スクリーンショット画像の画素位置ではなく、実際の画面位置と一致するように変換する必要があります。ここでの数値は、スクリーンショットがスクリーン座標に対して拡大された係数に相当します。|`3.12` for iOS, `1.0` otherwise|
|`ocrDownsampleFactor`|(Number) OCR を実行する前に、スクリーンショットをどの程度縮小するかを設定します。これを行う理由は、OCR アルゴリズムを高速化するためです。1.0`は縮小しないことを意味し、`2.0`は2倍縮小することを意味します。|`3.12` for iOS, `null` otherwise|
|`ocrInvertColors`|(Boolean) ダークモードの画面では、Tesseractは明るい背景と暗いテキストを想定しているので、色を反転させた方がよいでしょう。|`false`|
|`ocrContrast`|(Number) デフォルトでは、このプラグインはより良いOCR結果を得るために、画像のコントラストを上げようとします。この値は `-1.0` (コントラストを最大に下げる) と `1.0` (コントラストを最大に上げる) の間で設定することができます。`0.0`は、コントラスト調整を全く行わないことを意味します。|`0.5`|
|`ocrLanguage`|(String) Tesseract が学習データをダウンロードするための、 `+` 区切られた言語名のリスト。|`'eng'`|
|`ocrValidChars`|(String) OCRの際にTesseractが考慮すべき文字のリスト。特定の文字しか期待できないとわかっている場合は、独自のリストを記入することができ、精度と信頼性が向上する可能性があります。|`''`|

## Development

PRs welcomed!

### セットアップ

1. Clone repo
2. `npm install`

### Run tests

1. クローン先のプラグインをAppiumサーバーへインストールするのであれば、ルートフォルダーから `appium plugin install --source=local $(pwd)` を実行する。
2. Appium サーバーを起動する (e.g., `appium --use-plugins=ocr`)
3. `TEST_APP_PATH` 環境変数をエキスポートする。値には、TheApp.app.zip (https://github.com/cloudgrey-io/the-app/releases)の保存場所を保存する。
4. Javascript の場合：`npm run test:unit`
5. Javascript の場合：`npm run test:e2e`
6. Pythonの場合：`python appium_ocr_plugin_test.py`
