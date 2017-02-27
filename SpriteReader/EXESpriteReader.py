#!/usr/bin/python
# coding: utf-8

u''' EXE Sprite Reader  by ideal.exe


    データ構造仕様

    palData: パレットデータ辞書のリスト．OAMの生成（彩色）に使用する．
    palData[i] := { "color":[赤, 緑, 青, α], "addr":スプライト内のアドレス }

'''


import gettext
import os
import sys
import struct
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from PIL import Image
from PIL.ImageQt import ImageQt
_ = gettext.gettext # 後の翻訳用

import SpriteDict
sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), "../common/"))
import LZ77Util
import UI_EXESpriteReader as designer

from logging import getLogger,StreamHandler,INFO,DEBUG
logger = getLogger(__name__)    # 出力元の明確化
handler = StreamHandler()
handler.setLevel(INFO)
logger.setLevel(INFO)
logger.addHandler(handler)

import argparse
parser = argparse.ArgumentParser(description='対応しているROMのスプライトを表示します')
parser.add_argument("-f", "--file", help="開くROMファイル")
args = parser.parse_args()

""" 定数

    スプライトデータのフォーマットで決められている定数
"""
HEADER_SIZE = 4 # スプライトヘッダのサイズ
OFFSET_SIZE = 4
COLOR_SIZE  = 2 # 1色あたりのサイズ
FRAME_DATA_SIZE = 20
OAM_DATA_SIZE = 5
OAM_DATA_END = [b"\xFF\xFF\xFF\xFF\xFF", b"\xFF\xFF\xFF\xFF\x00"]
# フラグと形状の対応を取る辞書[size+shape]:[x,y]
OAM_DIMENSION = {
"0000":[8,8],
"0001":[16,8],
"0010":[8,16],
"0100":[16,16],
"0101":[32,8],
"0110":[8,32],
"1000":[32,32],
"1001":[32,16],
"1010":[16,32],
"1100":[64,64],
"1101":[64,32],
"1110":[32,64]
}

""" 設定用定数

    そのうちGUI上で設定できるようにするかもしれない定数
"""
EXPAND_ANIMATION_NUM = 64   # 拡張ダンプのアニメーション数
EXPAND_FRAME_NUM = 16   # 拡張ダンプのフレーム数


class SpriteReader(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = designer.Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.graphicsView.scale(2,2) # なぜかQt Designer上で設定できない

        self.romData = ""   # ファイルを読み込んだ時点でその内容がコピーされる．このデータを読み書きする．


    def openFile(self, filename=""):
        u''' ファイルを開くときの処理
        '''

        if filename == "":
            filename = QtWidgets.QFileDialog.getOpenFileName( self, _("Open EXE_ROM File"), os.path.expanduser('./') )[0]   # ファイル名とフィルタのタプルが返される

        try:
            with open( filename, 'rb' ) as romFile:
                self.romData = romFile.read()
        except:
            logger.info(u"ファイルが選択されませんでした")
            return -1

        if self.setSpriteDict(self.romData) == -1:
            u""" 非対応ROMの場合も中断
            """
            return -1

        self.extractSpriteAddr(self.romData)
        self.ui.spriteList.setCurrentRow(0)


    def openSprite(self):
        u""" スプライトファイルを開くときの処理
        """

        filename = QtWidgets.QFileDialog.getOpenFileName( self, _("Open EXE_Sprite File"), os.path.expanduser('./') )[0]   # ファイル名がQString型で返される

        try:
            with open( filename, 'rb' ) as romFile:
                self.romData = romFile.read()
        except:
            logger.info( _(u"ファイルの選択をキャンセルしました") )
            return -1

        self.spriteList = []
        self.ui.spriteList.clear()
        self.spriteList.append( {"spriteAddr":0, "compFlag":0, "readPos":0} )

        spriteItemStr = "Opened Sprite"  # GUIのリストに表示する文字列
        spriteItem = QtWidgets.QListWidgetItem( spriteItemStr )  # GUIのスプライトリストに追加するアイテムの生成
        self.ui.spriteList.addItem(spriteItem) # GUIスプライトリストへ追加
        self.ui.spriteList.setCurrentRow(0)  # 1番目のスプライトを自動で選択


    def setSpriteDict(self, romData):
        u""" バージョンを判定し使用する辞書をセットする
        """

        global romName
        romName = romData[0xA0:0xAC].decode("utf-8")
        global EXE_Addr    # アドレスリストはグローバル変数にする（書き換えないし毎回self.をつけるのが面倒なので）

        if romName == "ROCKEXE6_GXX":
            logger.info( _(u"ロックマンエグゼ6 グレイガ jp としてロードしました") )
            EXE_Addr = SpriteDict.ROCKEXE6_GXX
        elif romName == "MEGAMAN6_GXX":
            logger.info( _(u"ロックマンエグゼ6 グレイガ en としてロードしました") )
            EXE_Addr = SpriteDict.MEGAMAN6_GXX
        elif romName == "ROCKEXE6_RXX":
            logger.info( _(u"ロックマンエグゼ6 ファルザー jp としてロードしました") )
            EXE_Addr = SpriteDict.ROCKEXE6_RXX
        elif romName == "MEGAMAN6_FXX":
            logger.info( _(u"ロックマンエグゼ6 ファルザー en としてロードしました") )
            EXE_Addr = SpriteDict.MEGAMAN6_FXX

        elif romName == "ROCKEXE5_TOB":
            logger.info( _(u"ロックマンエグゼ5 チームオブブルース jp としてロードしました") )
            EXE_Addr = SpriteDict.ROCKEXE5_TOB
        elif romName == "ROCKEXE5_TOC":
            logger.info( _(u"ロックマンエグゼ5 チームオブカーネル jp としてロードしました") )
            EXE_Addr = SpriteDict.ROCKEXE5_TOC

        elif romName == "ROCKEXE4.5RO":
            logger.info( _(u"ロックマンエグゼ4.5 jp としてロードしました") )
            EXE_Addr = SpriteDict.ROCKEXE4_5RO

        elif romName == "ROCK_EXE4_RS":
            logger.info( _(u"ロックマンエグゼ4 トーナメントレッドサン jp としてロードしました") )
            EXE_Addr = SpriteDict.ROCKEXE4_RS
        elif romName == "ROCK_EXE4_BM":
            logger.info( _(u"ロックマンエグゼ4 トーナメントブルームーン jp としてロードしました") )
            EXE_Addr = SpriteDict.ROCKEXE4_BM

        elif romName == "ROCK_EXE3_BK":
            logger.info( _(u"ロックマンエグゼ3 Black jp としてロードしました") )
            EXE_Addr = SpriteDict.ROCK_EXE3_BK
        elif romName == "ROCKMAN_EXE3":
            logger.info(_(u"ロックマンエグゼ3 jp としてロードしました"))
            EXE_Addr = SpriteDict.ROCKMAN_EXE3

        elif romName == "ROCKMAN_EXE2":
            logger.info(_(u"ロックマンエグゼ2 jp としてロードしました"))
            EXE_Addr = SpriteDict.ROCKMAN_EXE2

        elif romName == "ROCKMAN_EXE\x00":
            logger.info(_(u"ロックマンエグゼ jp としてロードしました"))
            EXE_Addr = SpriteDict.ROCKMAN_EXE

        else:
            logger.info( _(u"対応していないバージョンです" ) )
            return -1   # error


    def extractSpriteAddr(self, romData):
        u''' スプライトのアドレスを抽出する

            スプライトリストが作成されます
            スプライトリストはスプライトのアドレス，圧縮状態，スプライトのアドレスを保持しているポインタのアドレスを保持します
            spriteListの各要素は{"spriteAddr":spriteAddr, "compFlag":compFlag, "pointerAddr":readPos}の形式です
        '''

        self.spriteList = []
        self.ui.spriteList.clear() # UIのスプライトリストの初期化

        readPos = EXE_Addr["startAddr"]
        while readPos <= EXE_Addr["endAddr"] - OFFSET_SIZE:
            u""" スプライトテーブルの読み込み

            テーブルの最後のアドレスはスプライトデータではなくデータの終端と思われる
            """

            spriteAddr = romData[readPos:readPos+OFFSET_SIZE]
            memByte = spriteAddr[3]

            if memByte in [0x08, 0x88]:
                u""" ポインタの最下位バイトはメモリ上の位置を表す0x08

                    0x88の場合は圧縮データとして扱われる模様
                """

                if memByte == 0x88: # ポインタ先頭が0x88なら圧縮スプライトとして扱う
                    compFlag = 1
                else:
                    compFlag = 0

                spriteAddr = int.from_bytes(spriteAddr[:3], "little")
                logger.debug("Sprite Address:\t" + hex(spriteAddr))

                if spriteAddr in EXE_Addr["ignoreAddr"]:
                    readPos += OFFSET_SIZE
                    continue

                self.spriteList.append( {"spriteAddr":spriteAddr, "compFlag":compFlag, "pointerAddr":readPos} )

                spriteAddrStr = ( hex(memByte)[2:].zfill(2) + hex(spriteAddr)[2:].zfill(6) ).upper() + "\t"  # GUIのリストに表示する文字列
                if romName == "ROCKEXE6_GXX":
                    try:
                        spriteAddrStr += SpriteDict.GXX_Sprite_List[hex(spriteAddr)]
                    except:
                        pass
                spriteItem = QtWidgets.QListWidgetItem( spriteAddrStr )  # GUIのスプライトリストに追加するアイテムの生成
                self.ui.spriteList.addItem(spriteItem) # GUIスプライトリストへ追加

            readPos += OFFSET_SIZE


    def guiSpriteItemActivated(self, index):
        u''' GUIでスプライトが選択されたときに行う処理

            描画シーンのクリア，アニメーションリストの生成
        '''

        if index == -1:
            u""" 何らかの原因で無選択状態になったら中断
            """
            return -1

        self.graphicsScene = QtWidgets.QGraphicsScene(self) # スプライトを描画するためのシーン（親がNULLだとメインウインドウが閉じたときに残ってアクセス違反を起こす）
        #self.graphicsScene.setSceneRect(-120,-80,240,160)    # gbaの画面を模したシーン（ ビューの中心が(0,0)になる ）
        self.ui.graphicsView.setScene(self.graphicsScene)
        self.ui.palSelect.setValue(0)   # パレットをリセット
        self.ui.animList.clear()

        spriteAddr = self.spriteList[index]["spriteAddr"]
        compFlag = self.spriteList[index]["compFlag"]

        [spriteData, animPtrList, frameDataList, oamDataList] = self.parseAllData(self.romData, spriteAddr, compFlag)
        self.spriteData = spriteData
        self.animPtrList = animPtrList
        self.frameDataList = frameDataList
        self.oamDataList = oamDataList

        self.ui.animLabel.setText(u"アニメーション：" + str(len(animPtrList)))
        for i, animPtr in enumerate(animPtrList):
            animPtrStr = str(i).zfill(2) + ":   " + hex(animPtr["value"])[2:].zfill(6).upper() # GUIに表示する文字列
            animItem = QtWidgets.QListWidgetItem( animPtrStr )    # GUIのアニメーションリストに追加するアイテムの生成
            self.ui.animList.addItem(animItem) # アニメーションリストへ追加
            logger.debug(hex(animPtr["value"]))

        self.ui.animList.setCurrentRow(0)   # self.guiAnimItemActivated(0)  が呼ばれる


    def parseAllData(self, romData, spriteAddr, compFlag):
        u""" スプライトの読み取り

            以下のリストを返す

            spriteData

            animPtrList.append({"animNum":animCount, "addr":readAddr, "value":animPtr})

            frameDataList.append({"animNum":animPtr["animNum"], "frameNum":frameCount, "address":readAddr, "frameData":frameData, \
                "graphSizeAddr":graphSizeAddr, "palSizeAddr":palSizeAddr, "junkDataAddr":junkDataAddr, \
                "oamPtrAddr":oamPtrAddr, "frameDelay":frameDelay, "frameType":frameType})

            oamDataList.append({"animNum":frameData["animNum"], "frameNum":frameData["frameNum"], "address":readAddr, "oamData":oamData})
        """

        if compFlag == 0:
            spriteData = romData[spriteAddr+HEADER_SIZE:]   # スプライトはサイズ情報を持たないので仮の範囲を切り出し
        elif compFlag == 1:
            spriteData = LZ77Util.decompLZ77_10(romData, spriteAddr)[8:]    # ファイルサイズ情報とヘッダー部分を取り除く
        else:
            logger.info(u"不明なエラーです")
            return -1

        readAddr = 0
        animDataStart = int.from_bytes(spriteData[readAddr:readAddr+OFFSET_SIZE], "little")
        logger.debug("Animation Data Start:\t" + hex(animDataStart))
        #animDataStart = struct.unpack("<L", animDataStart)[0]

        u""" アニメーションオフセットのテーブルからアニメーションのアドレスを取得
        """
        animPtrList = []
        animCount = 0
        while readAddr < animDataStart:
            animPtr = int.from_bytes(spriteData[readAddr:readAddr+OFFSET_SIZE], "little")
            logger.debug("Animation Pointer:\t" + hex(animPtr))
            #animPtr = struct.unpack("<L", animPtr)[0]
            animPtrList.append({"animNum":animCount, "addr":readAddr, "value":animPtr})
            readAddr += OFFSET_SIZE
            animCount += 1

        u""" アニメーションのアドレスから各フレームのデータを取得
        """
        frameDataList = []
        graphAddrList = []    # グラフィックデータは共有しているフレームも多いので別のリストで保持
        for i, animPtr in enumerate(animPtrList):
            readAddr = animPtr["value"]
            logger.debug("Animation " + str(i) + " at " + hex(readAddr))

            frameCount = 0
            while True: # do while文がないので代わりに無限ループ＋breakを使う
                frameData = spriteData[readAddr:readAddr+FRAME_DATA_SIZE]
                [graphSizeAddr, palSizeAddr, junkDataAddr, oamPtrAddr, frameDelay, frameType] = struct.unpack("<LLLLHH", frameData)   # データ構造に基づいて分解
                logger.debug("Frame Type:\t" + hex(frameType))
                if graphSizeAddr in [0x0000, 0x2000]:  # 流星のロックマンのスプライトを表示するための応急処置
                    logger.warning(u"不正なアドレスをロードしました．終端フレームが指定されていない可能性があります")
                    break

                if graphSizeAddr not in graphAddrList:
                    graphAddrList.append(graphSizeAddr)
                logger.debug("Graphics Size Address:\t" + hex(graphSizeAddr))

                try:
                    [graphicSize] = struct.unpack("L", spriteData[graphSizeAddr:graphSizeAddr+OFFSET_SIZE])
                except:
                    logger.warning(u"不正なアドレスをロードしました．終端フレームが指定されていない可能性があります")
                    break
                graphicData = spriteData[graphSizeAddr+OFFSET_SIZE:graphSizeAddr+OFFSET_SIZE+graphicSize]

                frameDataList.append({"animNum":animPtr["animNum"], "frameNum":frameCount, "address":readAddr, "frameData":frameData, \
                    "graphSizeAddr":graphSizeAddr, "graphicData":graphicData,"palSizeAddr":palSizeAddr, "junkDataAddr":junkDataAddr, \
                    "oamPtrAddr":oamPtrAddr, "frameDelay":frameDelay, "frameType":frameType})

                readAddr += FRAME_DATA_SIZE
                frameCount += 1

                if frameType in [0x80, 0xC0]: # 終端フレームならループを終了
                    break

        u""" フレームデータからOAMデータを取得
        """
        oamDataList = []
        for frameData in frameDataList:
            logger.debug("Frame at " + hex(frameData["address"]))
            logger.debug("  Animation Number:\t" + str(frameData["animNum"]))
            logger.debug("  Frame Number:\t\t" + str(frameData["frameNum"]))
            logger.debug("  Address of OAM Pointer:\t" + hex(frameData["oamPtrAddr"]))
            oamPtrAddr = frameData["oamPtrAddr"]
            [oamPtr] = struct.unpack("L", spriteData[oamPtrAddr:oamPtrAddr+OFFSET_SIZE])
            readAddr = oamPtrAddr + oamPtr

            while True:
                oamData = spriteData[readAddr:readAddr+OAM_DATA_SIZE]
                if oamData in OAM_DATA_END:
                    break
                logger.debug("OAM at " + hex(readAddr))
                logger.debug("OAM Data:\t" + str(oamData))

                [startTile, posX, posY, flag1, flag2] = struct.unpack("BbbBB", oamData)
                logger.debug("  Start Tile:\t" + str(startTile))
                logger.debug("  Offset X:\t" + str(posX))
                logger.debug("  Offset Y:\t" + str(posY))

                flag1 = bin(flag1)[2:].zfill(8)
                flag2 = bin(flag2)[2:].zfill(8)
                logger.debug("  Flag1 (VHNNNNSS)\t" + flag1)
                logger.debug("  Flag2 (PPPPNNSS)\t" + flag2)

                flipV = int( flag1[0], 2 ) # 垂直反転フラグ
                flipH = int( flag1[1], 2 ) # 水平反転フラグ

                palIndex = int(flag2[0:4], 2)

                objSize = flag1[-2:]
                objShape = flag2[-2:]
                [sizeX, sizeY] = OAM_DIMENSION[objSize+objShape]
                logger.debug("  Size X:\t" + str(sizeX))
                logger.debug("  Size Y:\t" + str(sizeY))

                oamDataList.append({"animNum":frameData["animNum"], "frameNum":frameData["frameNum"], "address":readAddr, "oamData":oamData, \
                    "startTile":startTile, "posX":posX, "posY":posY, "sizeX":sizeX, "sizeY":sizeY, "flipV":flipV, "flipH":flipH, "palIndex":palIndex})
                readAddr += OAM_DATA_SIZE

        u""" 無圧縮スプライトデータの切り出し
        """
        if compFlag == 0:
            endAddr = oamDataList[-1]["address"] + OAM_DATA_SIZE + len(OAM_DATA_END[0])
            spriteData = spriteData[:endAddr]

        return [spriteData, animPtrList, frameDataList, oamDataList]


    def guiAnimItemActivated(self, index):
        u''' GUIでアニメーションが選択されたときに行う処理

            フレームリストから選択されたアニメーションのフレームを取り出してリスト化
        '''

        if index == -1: # GUIの選択位置によっては-1が渡されることがある？
            return

        self.ui.frameList.clear()

        currentAnimFrame = [frame for frame in self.frameDataList if frame["animNum"] == index]
        self.ui.frameLabel.setText(u"フレーム：" + str(len(currentAnimFrame)))
        for i, frame in enumerate(currentAnimFrame):
            frameStr = str(i).zfill(2) + ":   " + hex(frame["address"])[2:].zfill(6).upper() + "\t" + str(frame["frameDelay"]) + "F\t"   # GUIに表示する文字列
            if frame["frameType"] == 128:
                frameStr += "Stop"
            elif frame["frameType"] == 192:
                frameStr += "Loop"
            frameItem = QtWidgets.QListWidgetItem( frameStr )    # GUIのフレームリストに追加するアイテムの生成
            self.ui.frameList.addItem(frameItem) # フレームリストへ追加

        self.ui.frameList.setCurrentRow(0)


    def guiFrameItemActivated(self, index):
        u''' GUIでフレームが選択されたときに行う処理

            現在のフレームのOAMを取得してリスト化，パレットの取得
        '''

        if index == -1:
            return

        self.graphicsScene.clear()  # 描画シーンのクリア
        self.ui.oamList.clear()
        animIndex = self.ui.animList.currentRow()

        u""" フレームが指定している色を無視してUIで選択中のパレットで表示する仕様にしています
        """
        palIndex = self.ui.palSelect.value()

        [currentFrame] = [frame for frame in self.frameDataList if frame["animNum"] == animIndex and frame["frameNum"] == index]
        self.parsePaletteData(self.spriteData, currentFrame["palSizeAddr"], palIndex)
        logger.debug("Palette Size Address:\t" + hex(currentFrame["palSizeAddr"]))

        currentFrameOam = [oam for oam in self.oamDataList if oam["animNum"] == animIndex and oam["frameNum"] == index]
        self.ui.oamLabel.setText(u"OAM：" + str(len(currentFrameOam)))

        for oam in currentFrameOam:
            oamAddrStr = ( hex(oam["address"])[2:].zfill(8)).upper()  # GUIのリストに表示する文字列
            oamItem = QtWidgets.QListWidgetItem( oamAddrStr )   # GUIのOAMリストに追加するアイテムの生成
            self.ui.oamList.addItem(oamItem) # GUIスプライトリストへ追加

            # OAM画像の生成，描画
            graphicData = currentFrame["graphicData"]
            image = self.makeOAMImage(graphicData, oam["startTile"], oam["sizeX"], oam["sizeY"], oam["flipV"], oam["flipH"])
            self.drawOAM(image, oam["sizeX"], oam["sizeY"], oam["posX"], oam["posY"])


    def parsePaletteData(self, spriteData, palSizePtr, palIndex):
        u''' パレットデータの読み取り

            入力：スプライトデータ，パレットサイズのアドレス
            処理：スプライトデータからのパレットサイズ読み込み，パレットデータ読み込み，RGBAカラー化
        '''

        # パレットサイズの読み取り
        palSize = spriteData[palSizePtr:palSizePtr+OFFSET_SIZE]
        palSize = struct.unpack("<L", palSize)[0]
        logger.debug("Palette Size:\t" + hex(palSize))
        if palSize != 0x20:  # サイズがおかしい場合は無視→と思ったら自作スプライトとかで0x00にしてることもあったので無視
            palSize = 0x20

        readPos = palSizePtr + OFFSET_SIZE + palIndex * palSize # パレットサイズ情報の後にパレットデータが続く（インデックス番号によって開始位置をずらす）
        endAddr = readPos + palSize

        self.palData = []    # パレットデータを格納するリスト
        self.ui.palList.clear()
        palCount = 0
        while readPos < endAddr:
            color = spriteData[readPos:readPos+COLOR_SIZE]
            color = struct.unpack("<H", color)[0]

            binColor = bin(color)[2:].zfill(16) # GBAのオブジェクトは15bitカラー（0BBBBBGGGGGRRRRR）
            logger.debug(bin(color)[2:].zfill(16))
            binB = int( binColor[1:6], 2 ) * 8  #   文字列化されているので数値に直す（255階調での近似色にするため8倍する）
            binG = int( binColor[6:11], 2 ) * 8
            binR = int( binColor[11:16], 2 ) * 8

            if palCount == 0:
                self.palData.append( {"color":[binR, binG, binB, 0], "addr":readPos } ) # 最初の色は透過色
            else:
                self.palData.append( {"color":[binR, binG, binB, 255], "addr":readPos } )

            colorStr = hex(color)[2:].zfill(4).upper() + "\t(" + str(binR).rjust(3) + ", " + str(binG).rjust(3) + ", " + str(binB).rjust(3) + ")"  # GUIに表示する文字列
            colorItem = QtWidgets.QListWidgetItem(colorStr)
            colorItem.setBackground( QtGui.QColor(binR, binG, binB) )  # 背景色をパレットの色に
            colorItem.setForeground( QtGui.QColor(255-binR, 255-binG, 255-binB) )    # 文字は反転色
            self.ui.palList.addItem(colorItem) # フレームリストへ追加

            palCount += 1
            readPos += COLOR_SIZE


    def changePalette(self, n):
        index = self.ui.frameList.currentRow()
        self.guiFrameItemActivated(index)


    def guiOAMItemActivated(self, item):
        u''' GUIでOAMが選択されたときに行う処理
        '''

        index = self.ui.oamList.currentRow()  # 渡されるのはアイテムなのでインデックス番号は現在の行から取得する
        logger.info("Serected OAM:\t" + str(index))
        items = self.graphicsScene.items()
        for item in items:
            logger.info(item)

        """
        oam = self.oamList[index]
        image = oam["image"]
        item = QtWidgets.QGraphicsPixmapItem(image)
        item.setOffset(oam["posX"], oam["posY"])
        imageBounds = item.boundingRect()
        self.graphicsScene.addRect(imageBounds)
        """


    def guiPalItemActivated(self, item):
        u''' GUIで色が選択されたときに行う処理
        '''

        index = self.ui.palList.currentRow()
        if index == -1:
            return -1

        r,g,b,a = self.palData[index]["color"]   # 選択された色の値をセット
        writePos = self.palData[index]["addr"]  # 色データを書き込む位置
        color = QtWidgets.QColorDialog.getColor( QtGui.QColor(r, g, b) )    # カラーダイアログを開く
        if color.isValid() == False: # キャンセルしたとき
            logger.info(u"色の選択をキャンセルしました")
            return 0

        r,g,b,a = color.getRgb()    # ダイアログでセットされた色に更新

        binR = bin(r//8)[2:].zfill(5)    # 5bitカラーに変換
        binG = bin(g//8)[2:].zfill(5)
        binB = bin(b//8)[2:].zfill(5)
        gbaColor = int(binB + binG + binR, 2)  # GBAのカラーコードに変換
        colorStr = struct.pack("H", gbaColor)
        self.spriteData = self.spriteData[:writePos] + colorStr + self.spriteData[writePos+COLOR_SIZE:]  # ロード中のスプライトデータの色を書き換える

        frameIndex = self.ui.frameList.currentRow()
        self.guiFrameItemActivated(frameIndex)


    def playAnimData(self):
        u''' アニメーションの再生
        '''

        logger.info(u"現在アニメーションの再生には対応していません")


    def makeOAMImage(self, imgData, startTile, width, height, flipV, flipH):
        u''' OAM情報から画像を生成する

            入力：スプライトのグラフィックデータ，開始タイル，横サイズ，縦サイズ，垂直反転フラグ，水平反転フラグ
            出力：画像データ（QPixmap形式）

            グラフィックデータは4bitで1pxを表現する．アクセス可能な最小単位は8*8pxのタイルでサイズは32byteとなる
        '''

        TILE_WIDTH = 8
        TILE_HEIGHT = 8
        TILE_DATA_SIZE = TILE_WIDTH * TILE_HEIGHT // 2  # python3で整数値の除算結果を得るには//を使う

        logger.debug("Image Width:\t" + str(width))
        logger.debug("Image Height:\t" + str(height))
        logger.debug("Flip V:\t" + str(flipV))
        logger.debug("Flip H:\t" + str(flipH))

        startAddr = startTile * TILE_DATA_SIZE  # 開始タイルから開始アドレスを算出（1タイル8*8px = 32バイト）
        imgData = imgData[startAddr:]   # 使う部分を切り出し
        imgData = (imgData.hex()).upper()   # バイナリ値をそのまま文字列にしたデータに変換（0xFF -> "FF"）
        imgData = list(imgData) # 1文字ずつのリストに変換
        # ドットの描画順（0x01 0x23 0x45 0x67 -> 10325476）に合わせて入れ替え
        for i in range(0, len(imgData))[0::2]:  # 偶数だけ取り出す（0から+2ずつ）
            imgData[i], imgData[i+1] = imgData[i+1], imgData[i] # これで値を入れ替えられる

        width = width // TILE_WIDTH # サイズからタイルの枚数に変換
        height = height // TILE_HEIGHT

        totalSize = len(imgData)    # 全ドット数
        imgArray = []

        # 色情報に変換する
        readPos = 0
        while readPos < totalSize:
            currentPixel = int(imgData[readPos], 16)    # 1ドット分読み込み
            imgArray.append(self.palData[currentPixel]["color"])    # 対応する色に変換
            readPos += 1

        imgArray = np.array(imgArray)   # ndarrayに変換
        imgArray = imgArray.reshape( (-1, TILE_WIDTH, 4) )  # 横8ドットのタイルに並べ替える（-1を設定すると自動で縦の値を算出してくれる）
        u""" 現在の状態

            □
            □
            ︙
            □
            □
        """

        tileNum = width * height  # 合計タイル数

        # タイルの切り出し
        tile = []  # pythonのリストとして先に宣言する（ndarrayとごっちゃになりやすい）
        for i in range(0, tileNum):
            tile.append(imgArray[TILE_HEIGHT*i:TILE_HEIGHT*(i+1), 0:TILE_WIDTH, :])    # 8x8のタイルを切り出していく

        # タイルの並び替え
        h = []  # 水平方向に結合したタイルを格納するリスト
        for i in range(0, height):
            h.append( np.zeros_like(tile[0]) )    # タイルを詰めるダミー
            for j in range(0, width):
                h[i] = np.hstack( (h[i], tile[i*width + j]) )
            if i != 0:
                h[0] = np.vstack((h[0], h[i]))
        img = h[0][:, 8:, :]    # ダミー部分を切り取る（ださい）

        dataImg = Image.fromarray( np.uint8(img) )  # 色情報の行列から画像を生成（PILのImage形式）
        if flipH == 1:
            dataImg = dataImg.transpose(Image.FLIP_LEFT_RIGHT)  # PILの機能で水平反転
        if flipV == 1:
            dataImg = dataImg.transpose(Image.FLIP_TOP_BOTTOM)
        qImg = ImageQt(dataImg) # QImage形式に変換
        pixmap = QtGui.QPixmap.fromImage(qImg)  # QPixmap形式に変換
        return pixmap


    def drawOAM(self, image, sizeX, sizeY, posX, posY):
        u''' OAMを描画する
        '''

        item = QtWidgets.QGraphicsPixmapItem(image)
        item.setOffset(posX , posY)
        #imageBounds = item.boundingRect()
        self.graphicsScene.addItem(item)
        #self.graphicsScene.addRect(imageBounds)


    def dumpSprite(self):
        u""" スプライトのダンプ
        """

        targetSprite = self.getCurrentSprite()

        if targetSprite["compFlag"] == 0:
            data = self.romData[targetSprite["spriteAddr"]:targetSprite["spriteAddr"]+HEADER_SIZE] + self.spriteData
        else:
            data = LZ77Util.decompLZ77_10(self.romData, targetSprite["spriteAddr"])[4:] # ファイルサイズ情報を取り除く

        filename = QtWidgets.QFileDialog.getSaveFileName(self, _(u"スプライトを保存する"), os.path.expanduser('./'), _("dump File (*.bin *.dmp)"))[0]
        try:
            with open( filename, 'wb') as saveFile:
                saveFile.write(data)
                logger.info(u"スプライトを保存しました")
        except:
            logger.info(u"スプライトの保存をキャンセルしました")


    def exDumpSprite(self):
        u""" スプライトを拡張してダンプ

            スプライトを32アニメーション，各16フレームのスペースを確保したスプライトに変換して保存する
            拡張した部分には停止フレームをコピーする
            アニメーション数が少ないスプライトを移植するときも安心
        """

        ANIMATION_TABLE_SIZE = EXPAND_ANIMATION_NUM * OFFSET_SIZE
        ANIMATION_SIZE = EXPAND_FRAME_NUM * FRAME_DATA_SIZE

        output = b"" # 出力用のスプライトデータ

        u""" アニメーションオフセットテーブル作成
        """
        animDataStart = EXPAND_ANIMATION_NUM * OFFSET_SIZE
        for i in range(EXPAND_ANIMATION_NUM):
            output += struct.pack("L", animDataStart + i * ANIMATION_SIZE)

        u""" グラフィック，OAMなどのコピー

            フレームデータ内で各アドレスを参照するので先にコピーする
        """
        output += b"\xFF" * ANIMATION_SIZE * EXPAND_ANIMATION_NUM # アニメーションデータ領域の確保
        writeAddr = ANIMATION_TABLE_SIZE + ANIMATION_SIZE * EXPAND_ANIMATION_NUM
        copyOffset = writeAddr - self.frameDataList[0]["graphSizeAddr"] # グラフィックデータの元の開始位置との差分（フレームデータの修正に使用する）
        # 先頭のフレームが先頭のグラフィックデータを使ってないパターンがあったら死ぬ
        output += self.spriteData[self.frameDataList[0]["graphSizeAddr"]:]  # グラフィックデータ先頭からスプライトの終端までコピー

        u""" アニメーション，フレームデータのコピー
        """
        for frameData in self.frameDataList:
            writeAddr = animDataStart + ANIMATION_SIZE * frameData["animNum"] + FRAME_DATA_SIZE * frameData["frameNum"]
            graphSizeAddr = frameData["graphSizeAddr"] + copyOffset
            palSizeAddr = frameData["palSizeAddr"] + copyOffset
            junkDataAddr = frameData["junkDataAddr"] + copyOffset
            oamPtrAddr = frameData["oamPtrAddr"] + copyOffset
            frameDelay = frameData["frameDelay"]
            frameType = frameData["frameType"]
            data = struct.pack("<LLLLHH", graphSizeAddr, palSizeAddr, junkDataAddr, oamPtrAddr, frameDelay, frameType)
            if frameType == 128:
                # ループしないフレームを拡張部分のダミーとして使う
                dummy = data
            output = output[:writeAddr] + data + output[writeAddr+len(data):]

        for i in range(len(self.animPtrList), EXPAND_ANIMATION_NUM):    # 拡張した部分のアニメーション
            u""" プラグイン時などはアニメーションが再生し終わらないと移動できないのでループアニメーションだと操作不能になってしまう
            """
            writeAddr = animDataStart + ANIMATION_SIZE * i
            output = output[:writeAddr] + dummy + output[writeAddr+len(dummy):]

        output = b"\xFF\xFF\xFF\xFF" + output    # ヘッダの追加

        filename = QtWidgets.QFileDialog.getSaveFileName(self, _(u"スプライトを保存する"), os.path.expanduser('./'), _("dump File (*.bin *.dmp)"))[0]
        try:
            with open( filename, 'wb') as saveFile:
                saveFile.write(output)
                logger.info(u"ファイルを保存しました")
        except:
            logger.info(u"ファイルの保存をキャンセルしました")


    def saveFrameImage(self):
        u""" フレーム画像の保存
        """

        sourceBounds = self.graphicsScene.itemsBoundingRect()    # シーン内の全てのアイテムから領域を算出
        #self.graphicsScene.addRect(sourceBounds)
        image = QtGui.QImage( QtCore.QSize(sourceBounds.width(), sourceBounds.height()), 6)
        image.fill(QtGui.QColor(0, 0, 0, 0).rgba()) # 初期化されていないのでfillしないとノイズが入る（えぇ・・・）
        targetBounds = QtCore.QRectF( image.rect() )
        painter = QtGui.QPainter(image)
        self.graphicsScene.render(painter, targetBounds, sourceBounds)
        painter.end()

        filename = QtWidgets.QFileDialog.getSaveFileName(self, _(u"フレーム画像を保存する"), os.path.expanduser('./'), _("image File (*.png)"))[0]
        try:
            image.save(filename, "PNG")
            logger.info(u"フレーム画像を保存しました")
        except:
            logger.info(u"ファイルの保存をキャンセルしました")


    def saveRomFile(self):
        u""" ファイルの保存
        """

        filename = QtWidgets.QFileDialog.getSaveFileName(self, _(u"ROMを保存する"), os.path.expanduser('./'), _("Rom File (*.gba *.bin)"))[0]
        try:
            with open( filename, 'wb') as saveFile:
                saveFile.write(self.romData)
                logger.info(u"ファイルを保存しました")
        except:
            logger.info(u"ファイルの保存をキャンセルしました")


    def repoint(self):
        u""" ポインタの書き換え
        """
        index = self.ui.spriteList.currentRow()
        targetAddr = self.spriteList[index]["pointerAddr"]
        logger.info( u"書き換えるアドレス：\t" + hex( targetAddr ) )

        dialog = QtWidgets.QDialog()
        dialog.ui = repointDialog()
        dialog.ui.setupUi(dialog)
        dialog.show()
        dialog.exec_()

        if dialog.result() == 1:
            addrText = dialog.ui.addrText.text()
            try:
                addr = int(str(addrText), 16)   # QStringから戻さないとダメ
                data = struct.pack("L", addr + 0x08000000)
                self.romData = self.romData[:targetAddr] + data + self.romData[targetAddr+len(data):]
                logger.info(u"スプライトポインタを書き換えました")
            except:
                logger.info(u"不正な値です")
            # リロード
            self.extractSpriteAddr(self.romData)
            self.ui.spriteList.setCurrentRow(index)
        else:
            logger.info(u"リポイントをキャンセルしました")

    def repointAnimation(self, item):
        u""" アニメーションポインタの書き換え
        """
        index = self.ui.animList.currentRow()
        if index == 0:
            logger.info(u"一つ目のアニメーションポインタはポインタテーブルのサイズに影響するので変更できません")
            return -1

        targetSprite = self.getCurrentSprite()
        if targetSprite["compFlag"] == 1:
            logger.info(u"現在圧縮スプライトのアニメーションリポイントは非対応です")
            return -1

        targetAddr = targetSprite["spriteAddr"] + HEADER_SIZE + self.animPtrList[index]["addr"]
        logger.info( u"書き換えるアドレス：\t" + hex( targetAddr ) )

        dialog = QtWidgets.QDialog()
        dialog.ui = repointDialog()
        dialog.ui.setupUi(dialog)
        dialog.show()
        dialog.exec_()

        if dialog.result() == 1:
            addrText = dialog.ui.addrText.text()
            try:
                addr = int(str(addrText), 16)   # QStringから戻さないとダメ
                data = struct.pack("L", addr)
                self.romData = self.romData[:targetAddr] + data + self.romData[targetAddr+len(data):]
                logger.info(u"アニメーションポインタを書き換えました")
            except:
                logger.info(u"不正な値です")
            # リロード
            spriteIndex = self.ui.spriteList.currentRow()
            if "EXE_Addr" in globals():
                self.extractSpriteAddr(self.romData)
            else:   # スプライトをロードした場合はアドレスリストが未定義になるので別途処理
                self.spriteList = []
                self.ui.spriteList.clear()
                self.spriteList.append( {"spriteAddr":0, "compFlag":0, "readPos":0} )

                spriteItemStr = "Opened Sprite"  # GUIのリストに表示する文字列
                spriteItem = QtWidgets.QListWidgetItem( spriteItemStr )  # GUIのスプライトリストに追加するアイテムの生成
                self.ui.spriteList.addItem(spriteItem) # GUIスプライトリストへ追加
            self.ui.spriteList.setCurrentRow(spriteIndex)
        else:
            logger.info(u"リポイントをキャンセルしました")


    def writePalData(self):
        u""" UI上で編集したパレットのデータをROMに書き込む
        """

        targetSprite = self.getCurrentSprite()
        if targetSprite["compFlag"] == 1:
            logger.info(u"圧縮スプライトは現在非対応です")
            return 0
        else:
            writeAddr = targetSprite["spriteAddr"] + HEADER_SIZE  # ヘッダのぶん4バイト
            self.romData = self.romData[:writeAddr] + self.spriteData + self.romData[writeAddr+len(self.spriteData):]
            logger.info(u"編集したパレットをメモリ上のROMに書き込みました")
            return 0


    def flipSprite(self):
        u""" 選択中のスプライトを水平反転する

            全てのOAMの水平反転フラグを切り替え，描画オフセットXを-X-sizeXにする
        """

        targetSprite = self.getCurrentSprite()
        if targetSprite["compFlag"] == 1:
            logger.info(u"圧縮スプライトは非対応です")
            return -1

        for oam in self.oamDataList:
            writeAddr = oam["address"] + targetSprite["spriteAddr"] + HEADER_SIZE   # ROM内でのアドレス
            logger.debug("OAM at " + hex(writeAddr) )
            oamData = oam["oamData"]
            [startTile, posX, posY, flag1, flag2] = struct.unpack("BbbBB", oamData)
            logger.debug("  Start Tile:\t" + str(startTile))
            logger.debug("  Offset X:\t" + str(posX))
            logger.debug("  Offset Y:\t" + str(posY))
            logger.debug("  Flag1 (VHNNNNSS)\t" + bin(flag1)[2:].zfill(8))
            logger.debug("  Flag2 (PPPPNNSS)\t" + bin(flag2)[2:].zfill(8))

            objSize = bin(flag1)[2:].zfill(8)[-2:]
            objShape = bin(flag2)[2:].zfill(8)[-2:]
            [sizeX, sizeY] = OAM_DIMENSION[objSize+objShape]
            logger.debug("  Size X:\t" + str(sizeX))
            logger.debug("  Size Y:\t" + str(sizeY))

            posX = posX * -1 -sizeX # 水平方向の描画座標を反転
            flag1 ^= 0b01000000 # 水平反転フラグをビット反転

            flipData = struct.pack("BbbBB", startTile, posX, posY, flag1, flag2)
            self.writeDataToRom(writeAddr, flipData)
            print(".", end="", flush=True)  # 必ず処理ごとに出力するようflush=Trueにする
        logger.info("done")

        logger.info(u"水平反転したスプライトを書き込みました")
        index = self.ui.spriteList.currentRow()
        self.guiSpriteItemActivated(index)


    def getCurrentSprite(self):
        u""" 選択中のスプライトを取得する
        """
        index = self.ui.spriteList.currentRow()
        if index == -1:
            return -1
        return self.spriteList[index]


    def writeDataToRom(self, writeAddr, data):
        u""" 指定したアドレスから指定したデータを上書きする
        """
        self.romData = self.romData[:writeAddr] + data + self.romData[writeAddr+len(data):]

    def changeViewScale(self, value):
        u""" ビューを拡大縮小する
        """
        self.ui.graphicsView.resetTransform()   # 一度オリジナルサイズに戻す
        scale = pow(2, value/10.0)   # 指数で拡大したほうが自然にスケールしてる感じがする
        self.ui.graphicsView.scale(scale, scale)

    def importSprite(self):
        u""" 指定したアドレスにファイルから読み込んだスプライトをインポートする
        """

        filename = QtWidgets.QFileDialog.getOpenFileName( self, _("Open EXE_Sprite File"), os.path.expanduser('./') )[0]   # ファイル名がQString型で返される

        try:
            with open( filename, 'rb' ) as spriteFile:
                spriteData = spriteFile.read()
        except:
            logger.info( _(u"ファイルの選択をキャンセルしました") )
            return -1

        dialog = QtWidgets.QDialog()
        dialog.ui = importDialog()
        dialog.ui.setupUi(dialog)
        dialog.show()
        dialog.exec_()

        if dialog.result() == 1:
            addrText = dialog.ui.addrText.text()
            try:
                addr = int(str(addrText), 16)   # QStringから戻さないとダメ
                if len(self.romData) < addr:
                    self.romData += "\xFF" * (addr - len(self.romData)) # 指定したアドレスまで0xFFで埋める
                self.writeDataToRom(addr, spriteData)
                logger.info(u"インポートに成功しました")
            except:
                logger.info(u"不正な値です")
            # リロード
            index = self.ui.spriteList.currentRow()
            self.extractSpriteAddr(self.romData)
            self.ui.spriteList.setCurrentRow(index)
        else:
            logger.info(u"インポートをキャンセルしました")


class repointDialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        Dialog.resize(300, 100)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.addrText = QtWidgets.QLineEdit(Dialog)
        self.addrText.setObjectName("addrText")
        self.verticalLayout.addWidget(self.addrText)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "リポイント"))
        self.label.setText(_translate("Dialog", "アドレス（16進数で指定してください）"))

class importDialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        Dialog.resize(300, 100)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.addrText = QtWidgets.QLineEdit(Dialog)
        self.addrText.setObjectName("addrText")
        self.verticalLayout.addWidget(self.addrText)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "インポート"))
        self.label.setText(_translate("Dialog", "アドレス（16進数で指定してください）"))

'''
main

'''
def main():
    app = QtWidgets.QApplication(sys.argv)

    spriteReader = SpriteReader();
    spriteReader.show()
    if args.file != None:
        spriteReader.openFile(args.file)

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

u'''
    フラグとサイズの関係．わかりづらい・・・

    shape:
        b00: 正方形
        b01: 長方形（横長）
        b10: 長方形（縦長）
        b11: 未使用

    size 0, shape 0: 8x8
    □
    size 0, shape 1: 16x8
    □□
    size 0, shape 2: 8x16
    □
    □
    size 1, shape 0: 16x16
    □□
    □□
    size 1, shape 1: 32x8
    □□□□
    size 1, shape 2: 8x32
    □
    □
    □
    □
    size 2, shape 0: 32x32
    □□□□
    □□□□
    □□□□
    □□□□
    size 2, shape 1: 32x16
    □□□□
    □□□□
    size 2, shape 2: 16x32
    □□
    □□
    □□
    □□
    size 3, shape 0: 64x64
    size 3, shape 1: 64x32
    size 3, shape 2: 32x64
'''