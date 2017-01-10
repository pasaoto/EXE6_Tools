#!/usr/bin/python
# coding: utf-8

u"""
    ロックマンエグゼ６の文字コードや各種アドレスの辞書

    ロックマンエグゼ６用文字コード対応表（http://www65.atwiki.jp/mmnbhack/pages/17.html）を少し改変
    エンコードでは文字コード対応表に基づく変換に加えて，解析のために独自の整形を行います．
    デコードではこれらの整形を行ったテキストが正しく元のバイナリと一致するように変換されます．

"""

import binascii
import sys

# 1バイト文字
CP_EXE6_1 = {
"\x00":" ",  "\x01":"０", "\x02":"１", "\x03":"２", "\x04":"３", "\x05":"４", "\x06":"５", "\x07":"６",
"\x08":"７", "\x09":"８", "\x0A":"９", "\x0B":"ウ", "\x0C":"ア", "\x0D":"イ", "\x0E":"オ", "\x0F":"エ",
"\x10":"ケ", "\x11":"コ", "\x12":"カ", "\x13":"ク", "\x14":"キ", "\x15":"セ", "\x16":"サ", "\x17":"ソ",
"\x18":"シ", "\x19":"ス", "\x1A":"テ", "\x1B":"ト", "\x1C":"ツ", "\x1D":"タ", "\x1E":"チ", "\x1F":"ネ",
"\x20":"ノ", "\x21":"ヌ", "\x22":"ナ", "\x23":"ニ", "\x24":"ヒ", "\x25":"ヘ", "\x26":"ホ", "\x27":"ハ",
"\x28":"フ", "\x29":"ミ", "\x2A":"マ", "\x2B":"メ", "\x2C":"ム", "\x2D":"モ", "\x2E":"ヤ", "\x2F":"ヨ",
"\x30":"ユ", "\x31":"ロ", "\x32":"ル", "\x33":"リ", "\x34":"レ", "\x35":"ラ", "\x36":"ン", "\x37":"熱",
"\x38":"斗", "\x39":"ワ", "\x3A":"ヲ", "\x3B":"ギ", "\x3C":"ガ", "\x3D":"ゲ", "\x3E":"ゴ", "\x3F":"グ",
"\x40":"ゾ", "\x41":"ジ", "\x42":"ゼ", "\x43":"ズ", "\x44":"ザ", "\x45":"デ", "\x46":"ド", "\x47":"ヅ",
"\x48":"ダ", "\x49":"ヂ", "\x4A":"ベ", "\x4B":"ビ", "\x4C":"ボ", "\x4D":"バ", "\x4E":"ブ", "\x4F":"ピ",
"\x50":"パ", "\x51":"ペ", "\x52":"プ", "\x53":"ポ", "\x54":"ゥ", "\x55":"ァ", "\x56":"ィ", "\x57":"ォ",
"\x58":"ェ", "\x59":"ュ", "\x5A":"ヴ", "\x5B":"ッ", "\x5C":"ョ", "\x5D":"ャ", "\x5E":"Ａ", "\x5F":"Ｂ",
"\x60":"Ｃ", "\x61":"Ｄ", "\x62":"Ｅ", "\x63":"Ｆ", "\x64":"Ｇ", "\x65":"Ｈ", "\x66":"Ｉ", "\x67":"Ｊ",
"\x68":"Ｋ", "\x69":"Ｌ", "\x6A":"Ｍ", "\x6B":"Ｎ", "\x6C":"Ｏ", "\x6D":"Ｐ", "\x6E":"Ｑ", "\x6F":"Ｒ",
"\x70":"Ｓ", "\x71":"Ｔ", "\x72":"Ｕ", "\x73":"Ｖ", "\x74":"Ｗ", "\x75":"Ｘ", "\x76":"Ｙ", "\x77":"Ｚ",
"\x78":"＊", "\x79":"－", "\x7A":"×", "\x7B":"＝", "\x7C":"：", "\x7D":"％", "\x7E":"？", "\x7F":"＋",
"\x80":"■", "\x81":"(ｺｳﾓﾘ)", "\x82":"ー", "\x83":"！", "\x84":"(RV)", "\x85":"(BX)", "\x86":"＆", "\x87":"、",
"\x88":"。", "\x89":"．", "\x8A":"・", "\x8B":"；", "\x8C":"’", "\x8D":"”", "\x8E":"～", "\x8F":"／",
"\x90":"（", "\x91":"）", "\x92":"「", "\x93":"」", "\x94":"(EX)", "\x95":"(SP)", "\x96":"(FZ)", "\x97":"□",
"\x98":"＿", "\x99":"ｚ", "\x9A":"周", "\x9B":"え", "\x9C":"お", "\x9D":"う", "\x9E":"あ", "\x9F":"い",
"\xA0":"け", "\xA1":"く", "\xA2":"き", "\xA3":"こ", "\xA4":"か", "\xA5":"せ", "\xA6":"そ", "\xA7":"す",
"\xA8":"さ", "\xA9":"し", "\xAA":"つ", "\xAB":"と", "\xAC":"て", "\xAD":"た", "\xAE":"ち", "\xAF":"ね",
"\xB0":"の", "\xB1":"な", "\xB2":"ぬ", "\xB3":"に", "\xB4":"へ", "\xB5":"ふ", "\xB6":"ほ", "\xB7":"は",
"\xB8":"ひ", "\xB9":"め", "\xBA":"む", "\xBB":"み", "\xBC":"も", "\xBD":"ま", "\xBE":"ゆ", "\xBF":"よ",
"\xC0":"や", "\xC1":"る", "\xC2":"ら", "\xC3":"り", "\xC4":"ろ", "\xC5":"れ", "\xC6":"究", "\xC7":"ん",
"\xC8":"を", "\xC9":"わ", "\xCA":"研", "\xCB":"げ", "\xCC":"ぐ", "\xCD":"ご", "\xCE":"が", "\xCF":"ぎ",
"\xD0":"ぜ", "\xD1":"ず", "\xD2":"じ", "\xD3":"ぞ", "\xD4":"ざ", "\xD5":"で", "\xD6":"ど", "\xD7":"づ",
"\xD8":"だ", "\xD9":"ぢ", "\xDA":"べ", "\xDB":"ば", "\xDC":"び", "\xDD":"ぼ", "\xDE":"ぶ", "\xDF":"ぽ",
"\xE0":"ぷ", "\xE1":"ぴ", "\xE2":"ぺ", "\xE3":"ぱ",
"\xE4":"<E4>",    "\xE5":"<E5>",    "\xE6":"<E6:閉>",    "\xE7":"<E7:終端>",
"\xE8":"<E8:開>",    "\xE9":"<E9:改行>",    "\xEA":"<EA>",    "\xEB":"<EB>",
"\xEC":"<EC:Cursor>",    "\xED":"<ED:Select>",    "\xEE":"<EE:Pause>",    "\xEF":"<skip?>",
"\xF0":"<F0:ch_speaker>",    "\xF1":"<F1:Speed>",    "\xF2":"<F2:消去>",    "\xF3":"<F3>",
"\xF4":"<F4:Sound>",    "\xF5":"<F5:顔>",    "\xF6":"<F6>",    "\xF7":"<F7>",
"\xF8":"<F8>",    "\xF9":"<F9>",    "\xFA":"<FA>",    "\xFB":"<FB>",
"\xFC":"<FC>",    "\xFD":"<FD>",    "\xFE":"<FE>",    "\xFF":"<FF>"
}

# 2バイト文字（\xE4 + \xXX）
CP_EXE6_2 = {
"\x00":"ぅ",    "\x01":"ぁ",    "\x02":"ぃ",    "\x03":"ぉ",    "\x04":"ぇ",    "\x05":"ゅ",    "\x06":"ょ",    "\x07":"っ",
"\x08":"ゃ",    "\x09":"a",    "\x0A":"b",    "\x0B":"c",    "\x0C":"d",    "\x0D":"e",    "\x0E":"f",    "\x0F":"g",
"\x10":"h",    "\x11":"i",    "\x12":"j",    "\x13":"k",    "\x14":"l",    "\x15":"m",    "\x16":"n",    "\x17":"o",
"\x18":"p",    "\x19":"q",    "\x1A":"r",    "\x1B":"s",    "\x1C":"t",    "\x1D":"u",    "\x1E":"v",    "\x1F":"w",
"\x20":"x",    "\x21":"y",    "\x22":"z",    "\x23":"容",    "\x24":"量",    "\x25":"全",    "\x26":"木",    "\x27":"(MB)",
"\x28":"無",    "\x29":"現",    "\x2A":"実",    "\x2B":"○",    "\x2C":"×",    "\x2D":"緑",    "\x2E":"道",    "\x2F":"不",
"\x30":"止",    "\x31":"彩",    "\x32":"起",    "\x33":"父",    "\x34":"集",    "\x35":"院",    "\x36":"一",    "\x37":"二",
"\x38":"三",    "\x39":"四",    "\x3A":"五",    "\x3B":"六",    "\x3C":"七",    "\x3D":"八",    "\x3E":"陽",    "\x3F":"十",
"\x40":"百",    "\x41":"千",    "\x42":"万",    "\x43":"脳",    "\x44":"上",    "\x45":"下",    "\x46":"左",    "\x47":"右",
"\x48":"手",    "\x49":"来",    "\x4A":"日",    "\x4B":"目",    "\x4C":"月",    "\x4D":"獣",    "\x4E":"名",    "\x4F":"人",
"\x50":"入",    "\x51":"出",    "\x52":"山",    "\x53":"口",    "\x54":"光",    "\x55":"電",    "\x56":"気",    "\x57":"綾",
"\x58":"科",    "\x59":"次",    "\x5A":"名",    "\x5B":"前",    "\x5C":"学",    "\x5D":"校",    "\x5E":"省",    "\x5F":"祐",
"\x60":"室",    "\x61":"世",    "\x62":"界",    "\x63":"高",    "\x64":"朗",    "\x65":"枚",    "\x66":"野",    "\x67":"悪",
"\x68":"路",    "\x69":"闇",    "\x6A":"大",    "\x6B":"小",    "\x6C":"中",    "\x6D":"自",    "\x6E":"分",    "\x6F":"間",
"\x70":"系",    "\x71":"鼻",    "\x72":"問",    "\x73":"究",    "\x74":"門",    "\x75":"城",    "\x76":"王",    "\x77":"兄",
"\x78":"化",    "\x79":"葉",    "\x7A":"行",    "\x7B":"街",    "\x7C":"屋",    "\x7D":"水",    "\x7E":"見",    "\x7F":"終",
"\x80":"新",    "\x81":"桜",    "\x82":"先",    "\x83":"生",    "\x84":"長",    "\x85":"今",    "\x86":"了",    "\x87":"点",
"\x88":"井",    "\x89":"子",    "\x8A":"言",    "\x8B":"太",    "\x8C":"属",    "\x8D":"風",    "\x8E":"会",    "\x8F":"性",
"\x90":"持",    "\x91":"時",    "\x92":"勝",    "\x93":"赤",    "\x94":"毎",    "\x95":"年",    "\x96":"火",    "\x97":"改",
"\x98":"計",    "\x99":"画",    "\x9A":"職",    "\x9B":"体",    "\x9C":"波",    "\x9D":"回",    "\x9E":"外",    "\x9F":"地",
"\xA0":"員",    "\xA1":"正",    "\xA2":"造",    "\xA3":"値",    "\xA4":"合",    "\xA5":"戦",    "\xA6":"川",    "\xA7":"秋",
"\xA8":"原",    "\xA9":"町",    "\xAA":"晴",    "\xAB":"用",    "\xAC":"金",    "\xAD":"郎",    "\xAE":"作",    "\xAF":"数",
"\xB0":"方",    "\xB1":"社",    "\xB2":"攻",    "\xB3":"撃",    "\xB4":"力",    "\xB5":"同",    "\xB6":"武",    "\xB7":"何",
"\xB8":"発",    "\xB9":"少",    "\xBA":"教",    "\xBB":"以",    "\xBC":"白",    "\xBD":"早",    "\xBE":"暮",    "\xBF":"面",
"\xC0":"組",    "\xC1":"後",    "\xC2":"文",    "\xC3":"字",    "\xC4":"本",    "\xC5":"階",    "\xC6":"明",    "\xC7":"才",
"\xC8":"者",    "\xC9":"向",    "\xCA":"犬",    "\xCB":"々",    "\xCC":"ヶ",    "\xCD":"連",    "\xCE":"射",    "\xCF":"舟",
"\xD0":"戸",    "\xD1":"切",    "\xD2":"土",    "\xD3":"炎",    "\xD4":"伊",    "\xD5":"夫",    "\xD6":"鉄",    "\xD7":"国",
"\xD8":"男",    "\xD9":"天",    "\xDA":"老",    "\xDB":"師",    "\xDC":"xDC",    "\xDD":"xDD",    "\xDE":"xDE",    "\xDF":"xDF",
"\xE0":"xE0",    "\xE1":"xE1",    "\xE2":"xE2",    "\xE3":"xE3",    "\xE4":"xE4",    "\xE5":"xE5",    "\xE6":"xE6",    "\xE7":"xE7",
"\xE8":"xE8",    "\xE9":"xE9",    "\xEA":"xEA",    "\xEB":"xEB",    "\xEC":"xEC",    "\xED":"xED",    "\xEE":"xEE",    "\xEF":"xEF",
"\xF0":"xF0",    "\xF1":"xF1",    "\xF2":"xF2",    "\xF3":"xF3",    "\xF4":"xF4",    "\xF5":"xF5",    "\xF6":"xF6",    "\xF7":"xF7",
"\xF8":"xF8",    "\xF9":"xF9",    "\xFA":"xFA",    "\xFB":"xFB",    "\xFC":"xFC",    "\xFD":"xFD",    "\xFE":"xFE",    "\xFF":"xFF"
}

# 逆引き辞書
CP_EXE6_1_inv = {v:k for k, v in CP_EXE6_1.items()}
CP_EXE6_2_inv = {v:k for k, v in CP_EXE6_2.items()}

# テキストからバイナリに変換するときに半角にも対応する
half = {
"0":"\x01",    "1":"\x02",    "2":"\x03",    "3":"\x04",    "4":"\x05",
"5":"\x06",    "6":"\x07",    "7":"\x08",    "8":"\x09",    "9":"\x0A",
"A":"\x5E",    "B":"\x5F",    "C":"\x60",    "D":"\x61",    "E":"\x62",
"F":"\x63",    "G":"\x64",    "H":"\x65",    "I":"\x66",    "J":"\x67",
"K":"\x68",    "L":"\x69",    "M":"\x6A",    "N":"\x6B",    "O":"\x6C",
"P":"\x6D",    "Q":"\x6E",    "R":"\x6F",    "S":"\x70",    "T":"\x71",
"U":"\x72",    "V":"\x73",    "W":"\x74",    "X":"\x75",    "Y":"\x76",
"Z":"\x77",    "*":"\x78",    "-":"\x79",    "=":"\x7B",    ":":"\x7C",
"%":"\x7D",    "?":"\x7E",    "+":"\x7F",    "!":"\x83",    "&":"\x86",
}
CP_EXE6_1_inv.update(half)

# グレイガ版の各種アドレス[名前, 先頭アドレス, 終端アドレス]
GXX_Addr_List = [
["Map",      "0x6EB560", "0x6EBC09"],
["ChipText", "0x70C36E", "0x7102A2"],
["Enemy",    "0x710FFE", "0x71163F"],
["Navi",     "0x7117B0", "0x711B7F"],
["KeyItem",  "0x75F094", "0x75F37A"],
["NaviCus",  "0x75FF39", "0x7600A0"]
]

# ロックマンのスプライトのポインタ周辺をとりあえず使ってみる
# このアドレスの直前にポインタのテーブルっぽいものがある
# テーブルのポインタが示すアドレスには白玉がある．スプライトのまとまりを区切ってるのだろうか
GXX_Sprite_Table = {
"startAddr":0x032CA8,
"endAddr":0x033963
}

GXX_Sprite_List = {
u""" グレイガ版の各スプライトの先頭アドレスと内容
"""

"0x1d8000":"ロックマン（戦闘）",
"0x1df420":"ヒートビースト（戦闘）",
"0x1e7cc8":"エレキビースト（戦闘）",
"0x1f1414":"スラッシュビースト（戦闘）",
"0x1fa9e8":"キラービースト（戦闘）",
"0x204108":"チャージビースト（戦闘）",
"0x20cd4c":"アクアビースト（戦闘）",
"0x214808":"トマホークビースト（戦闘）",
"0x21c354":"テングビースト（戦闘）",
"0x223c48":"グランドビースト（戦闘）",
"0x22cc50":"ダストビースト（戦闘）",
"0x233728":"グレイガビースト（戦闘）",
"0x23b768":"ファルザービースト（戦闘）",
"0x4ea2e4":"白玉",
"0x241ec4":"メットール（戦闘）",
"0x242e94":"アーバルボーイ（戦闘）",
"0x244164":"メガリア（戦闘）",
"0x2455b0":"スウォーディン（戦闘）",
"0x246a24":"キラーズアイ（戦闘）",
"0x2489c8":"クエイカー（戦闘）",
"0x2492fc":"キャタック（戦闘）",
"0x249c7c":"チャンプル（戦闘）",
"0x24ac94":"ウインドボックス（戦闘）",
"0x24b254":"ララパッパ（戦闘）",
"0x24d23c":"ダルスト（戦闘）",
"0x24dc7c":"ドルダーラ（戦闘）",
"0x24eaf4":"ヤカーン（戦闘）",
"0x252558":"センボン（戦闘）",
"0x2533f4":"ヒトデスタ（戦闘）",
"0x253f88":"ツボリュウ（戦闘）",
"0x257994":"カカジー（戦闘）",
"0x25859c":"パルフォロン（戦闘）",
"0x258ff8":"グラサン（戦闘）",
"0x25a0d8":"ボムコーン（戦闘）",
"0x25ad90":"モリキュー（戦闘）",
"0x25b860":"ハニホー（戦闘）",
"0x25bfc4":"ガンナー（戦闘）",
"0x25c9ac":"ゼロプレーン（戦闘）",
"0x25dfb4":"アサシンメカ（戦闘）",
"0x25f2c8":"スナーム（戦闘）",
"0x260f88":"アルマン（戦闘）",
"0x262cec":"レムゴン（戦闘）",
"0x263484":"ナイトメア（戦闘）",
"0x2647e4":"トーテム様（戦闘）",
"0x264fa0":"ヒートマン（戦闘）",
"0x26faf0":"エレキマン（戦闘）",
"0x278ebc":"スラッシュマン（戦闘）",
"0x28324c":"キラーマン（戦闘）",
"0x28f18c":"チャージマン（戦闘）",
"0x296f40":"アクアマン（戦闘）",
"0x29d818":"トマホークマン（戦闘）",
"0x2a5af0":"テングマン（戦闘）",
"0x2b0690":"グランドマン（戦闘）",
"0x2ba7bc":"ダストマン（戦闘）",
"0x2c7550":"ブルース（戦闘）",
"0x2ced74":"ブラストマン（戦闘）",
"0x2d2ac8":"ダイブマン（戦闘）",
"0x2d6fe4":"サーカスマン（戦闘）",
"0x2dabc8":"ジャッジマン（戦闘）",
"0x2dd9a8":"エレメントマン（戦闘）",
"0x2e0114":"カーネル（戦闘）",
"0x2e4050":"フォルテ（戦闘）",
"0x2e8470":"グレイガ（戦闘）",
"0x4ea9dc":"白玉",
"0x2ef3c0":"ハクシャク（戦闘）",
"0x2f279c":"ソード（戦闘）",
"0x2f6314":"キャノン（戦闘）",
"0x2f7ff0":"ボム（戦闘）",
"0x2f9820":"バスター（戦闘）",
"0x2fc620":"ヒートクロス（戦闘）",
"0x2ff368":"獣化（戦闘）",
"0x300ccc":"マズルフラッシュ（戦闘）",
"0x301058":"オーラ（戦闘）",
"0x3022b0":"センシャホウ（戦闘）",
"0x303650":"ビーストカーソル（戦闘）",
"0x3038c4":"ファルザービーストの羽（戦闘）",
"0x306388":"ヨーヨー（戦闘）",
"0x306e70":"ヨーヨー手元（戦闘）",
"0x307054":"トマホーククロス（戦闘）",
"0x30b054":"炎（戦闘）",
"0x30b980":"ジャンゴ（戦闘）",
"0x30db4c":"アクアショット（戦闘）",
"0x30ee28":"ダストクロス（戦闘）",
"0x311fb4":"",
"0x312f6c":"",
"0x313c64":"",
"0x315da8":"",
"0x317008":"",
"0x317ad4":"",
"0x3183e4":"",
"0x319e2c":"",
"0x31b13c":"",
"0x31be60":"",
"0x31d440":"",
"0x31e110":"",
"0x31e67c":"",
"0x3213c4":"",
"0x321618":"",
"0x32319c":"",
"0x3233e0":"",
"0x323560":"",
"0x3245a4":"",
"0x324810":"",
"0x32606c":"",
"0x327440":"",
"0x327ff4":"",
"0x328248":"",
"0x328d14":"",
"0x329108":"",
"0x3294d0":"",
"0x329934":"",
"0x329b58":"",
"0x32a0e0":"",
"0x32a7b4":"",
"0x32aa14":"",
"0x32ade0":"",
"0x32b244":"",
"0x32c4e0":"",
"0x32e848":"",
"0x330f38":"",
"0x3334e8":"",
"0x333be8":"",
"0x3343e8":"",
"0x335550":"",
"0x335ac8":"",
"0x336310":"",
"0x336dd8":"",
"0x336fa4":"",
"0x337e70":"",
"0x3387e8":"",
"0x33962c":"",
"0x339cbc":"",
"0x33a5a4":"",
"0x33b4d0":"",
"0x33bf04":"",
"0x33d320":"ロール（戦闘）",
"0x33e0c8":"エレキクロス（戦闘）",
"0x341018":"スラッシュクロス（戦闘）",
"0x344550":"テングクロス（戦闘）",
"0x347c74":"キラークロス（戦闘）",
"0x34ae00":"チャージクロス（戦闘）",
"0x34e030":"",
"0x34e97c":"",
"0x34f2b8":"",
"0x34f730":"",
"0x350044":"",
"0x350480":"",
"0x350854":"",
"0x350da0":"",
"0x351068":"",
"0x3518a0":"",
"0x354df0":"",
"0x3557d8":"",
"0x357204":"",
"0x357464":"",
"0x3592a4":"",
"0x35a9c4":"",
"0x35ad7c":"",
"0x35c0d8":"",
"0x35d1c0":"",
"0x35d728":"",
"0x35d90c":"",
"0x35e76c":"",
"0x35eb58":"",
"0x35f110":"",
"0x35fd24":"",
"0x36052c":"",
"0x362060":"",
"0x3637b8":"",
"0x364354":"",
"0x364ecc":"",
"0x3651b0":"",
"0x365448":"",
"0x366c80":"",
"0x367e40":"",
"0x3691ec":"",
"0x369c18":"",
"0x3705d8":"",
"0x371ce4":"",
"0x374438":"",
"0x3745a8":"",
"0x3753f8":"",
"0x376dc4":"",
"0x377820":"",
"0x377b48":"",
"0x379afc":"",
"0x37a004":"",
"0x37a9e0":"",
"0x37b1a0":"",
"0x37bcc4":"",
"0x37c03c":"",
"0x37c88c":"",
"0x37cb00":"",
"0x37f0f4":"",
"0x37f7b4":"",
"0x3805c4":"",
"0x380884":"",
"0x382ad4":"",
"0x386670":"",
"0x3878dc":"",
"0x388070":"",
"0x388b28":"",
"0x389364":"",
"0x38a0d0":"",
"0x38b080":"",
"0x38b6b8":"",
"0x38c428":"",
"0x38e0e4":"",
"0x38e3d8":"",
"0x38f284":"",
"0x38ffd4":"",
"0x390bdc":"",
"0x39122c":"",
"0x393738":"",
"0x393ef0":"",
"0x3941c8":"",
"0x3946c0":"",
"0x395158":"",
"0x3955f4":"",
"0x396f24":"",
"0x3974dc":"",
"0x397990":"",
"0x399634":"",
"0x399cd4":"",
"0x399d54":"",
"0x39abd0":"",
"0x39b20c":"",
"0x39be70":"",
"0x39ddc4":"",
"0x39e3f0":"",
"0x39f3e0":"",
"0x39ff50":"",
"0x3a0dd8":"",
"0x3a2308":"",
"0x3a3848":"",
"0x3a4750":"",
"0x3a5a6c":"",
"0x3a8d9c":"",
"0x3a9b38":"",
"0x3aebc0":"",
"0x3af53c":"",
"0x3b1f20":"",
"0x3b4f38":"",
"0x3b51c0":"",
"0x3b5cd8":"",
"0x3b6600":"",
"0x3b7044":"",
"0x3b83e8":"",
"0x3b8e88":"",
"0x3b9820":"",
"0x3bb224":"",
"0x3bc984":"",
"0x3bd19c":"",
"0x3bd874":"",
"0x3becd4":"",
"0x3c2044":"",
"0x3c25b4":"",
"0x3c3c40":"",
"0x3c4740":"",
"0x3c56b0":"",
"0x3c5f70":"",
"0x3c6528":"",
"0x3c79b0":"",
"0x3c900c":"",
"0x3d6874":"",
"0x3d9228":"",
"0x3dc76c":"",
"0x3df34c":"",
"0x3e24c0":"",
"0x3e63a8":"",
"0x3e9408":"",
"0x3eb1ec":"",
"0x3ebe48":"",
"0x3ee8f8":"",
"0x3f124c":"",
"0x3f4c80":"",
"0x3f8214":"",
"0x3fcac4":"",
"0x3ffb24":"",
"0x403430":"",
"0x40727c":"",
"0x407f68":"",
"0x40c2a0":"",
"0x40f344":"",
"0x40fcec":"",
"0x411660":"",
"0x4120b4":"",
"0x4137bc":"",
"0x413f00":"",
"0x4146a4":"",
"0x4187f4":"",
"0x419a70":"",
"0x419f14":"",
"0x41ab64":"",
"0x41b02c":"",
"0x41b444":"",
"0x41f044":"",
"0x4229f4":"",
"0x425f78":"",
"0x429760":"",
"0x42e22c":"",
"0x433be4":"",
"0x437074":"",
"0x439ae8":"",
"0x43a388":"",
"0x43c40c":"",
"0x43cec4":"",
"0x446f3c":"",
"0x447818":"",
"0x44832c":"",
"0x448bc4":"",
"0x44eaf4":"",
"0x452790":"",
"0x458910":"",
"0x460720":"",
"0x46344c":"",
"0x46b90c":"",
"0x4710b0":"",
"0x47d090":"",
"0x484e80":"",
"0x48e020":"",
"0x48fe24":"",
"0x492a4c":"",
"0x49c7c4":"",
"0x4a1f0c":"",
"0x4a2660":"",
"0x4a47d0":"",
"0x4a6200":"",
"0x4a6fe0":"",
"0x4a7934":"",
"0x4a7f38":"",
"0x4a9674":"",
"0x4aaa5c":"",
"0x4ac0d0":"",
"0x4ac8c8":"",
"0x4ace30":"",
"0x4ad2dc":"",
"0x4ad968":"",
"0x4ae024":"",
"0x4ae340":"",
"0x4ae76c":"",
"0x4ae9dc":"",
"0x4af558":"",
"0x4afc18":"",
"0x4b0054":"",
"0x4b0318":"",
"0x4b05f0":"",
"0x4b0d00":"",
"0x4b141c":"",
"0x4b153c":"",
"0x4b18d4":"",
"0x4b1eac":"",
"0x4b293c":"",
"0x4b3224":"",
"0x4b36b0":"",
"0x4b39b4":"",
"0x4b3cb4":"",
"0x4b3f24":"",
"0x4b44b4":"",
"0x4b4a34":"",
"0x4b4fd0":"",
"0x4b536c":"",
"0x4b5814":"",
"0x4b59f8":"",
"0x4b5f64":"",
"0x4b6054":"",
"0x4b68d4":"",
"0x4b6eec":"",
"0x4b752c":"",
"0x4b771c":"",
"0x4b77c4":"",
"0x4b7b7c":"",
"0x4b7f2c":"",
"0x4ba618":"",
"0x4babec":"",
"0x4bbfbc":"",
"0x4be44c":"",
"0x4c0b98":"",
"0x4c10e4":"",
"0x4c1ae4":"",
"0x4c1fe0":"",
"0x4c24c4":"",
"0x4c2b58":"",
"0x4c2ff0":"",
"0x4c3cc0":"",
"0x4c5460":"",
"0x4c6cc0":"",
"0x4c7054":"",
"0x4c76a4":"",
"0x4c7928":"",
"0x4c7fb0":"",
"0x4c8320":"",
"0x4c8974":"",
"0x4c8d7c":"",
"0x4c9100":"",
"0x4c9ca8":"",
"0x4ca0e8":"",
"0x4ca680":"",
"0x4cb1d0":"",
"0x4cb588":"",
"0x4cb7f8":"",
"0x4cbd7c":"",
"0x4cc7d4":"",
"0x4cc91c":"",
"0x4cf3b8":"",
"0x4d0314":"",
"0x4d05d8":"",
"0x4d0a30":"",
"0x4d1818":"",
"0x4d22d8":"",
"0x4d25a0":"",
"0x4d36a8":"",
"0x4d3c38":"",
"0x4d3ee8":"",
"0x4d4270":"",
"0x4d4768":"",
"0x4d4aec":"",
"0x4d4da0":"",
"0x4d5030":"",
"0x4d5328":"",
"0x4d5614":"",
"0x4d5be0":"",
"0x4d5dac":"",
"0x4d62cc":"",
"0x4d6870":"",
"0x4d7800":"",
"0x4d9264":"",
"0x4d9734":"",
"0x4db8f4":"",
"0x4dba40":"",
"0x4dbdf0":"",
"0x4dbf54":"",
"0x4dc188":"",
"0x4dd0cc":"",
"0x4dd4f0":"",
"0x4dd744":"",
"0x4dd898":"",
"0x4de5a0":"",
"0x4de7ac":"",
"0x4dead4":"",
"0x4df248":"",
"0x4df3a4":"",
"0x4df924":"",
"0x4dfc6c":"",
"0x4e0008":"",
"0x4e0258":"",
"0x4e0540":"",
"0x4e07a0":"",
"0x4e096c":"",
"0x4e1678":"",
"0x4e24d8":"",
"0x4e2ae8":"",
"0x4e301c":"",
"0x4e3ccc":"",
"0x4e43dc":"",
"0x4e4714":"",
"0x4e4894":"",
"0x4e4fc0":"",
"0x4e53f8":"",
"0x4e5978":"",
"0x4e62a0":"",
"0x4e68d4":"",
"0x4e6ad4":"",
"0x4e7480":"",
"0x4e7688":"",
"0x4e7864":"",
"0x4e7bf8":"",
"0x4e7e68":"",
"0x4e7ff8":"",
"0x4e84b8":"",
"0x4e8d68":"",
"0x4e9404":"",
"0x4e96fc":"",
"0x4e9e30":"",
"0x4eabf8":"",
"0x4eb380":"",
"0x4eba60":"",
"0x4ec270":"",
"0x4ec8d0":"",
"0x4ecf90":"",
"0x4ed5b0":"",
"0x506328":"",
"0x4edc10":"",
"0x4ee25c":"",
"0x4ee83c":"",
"0x4eed58":"",
"0x4ef358":"",
"0x4ef9dc":"",
"0x4effd4":"",
"0x4f0594":"",
"0x4f0c34":"",
"0x4f1270":"",
"0x4f1890":"",
"0x4f1eb0":"",
"0x4f2590":"",
"0x4f2bf0":"",
"0x4f31f0":"",
"0x4f37a8":"",
"0x4f3dac":"",
"0x4f43ac":"",
"0x4f4a6c":"",
"0x4f50b8":"",
"0x4f57d8":"",
"0x4f5d74":"",
"0x4f63d4":"",
"0x4f6b74":"",
"0x4f7334":"",
"0x4f799c":"",
"0x4f80bc":"",
"0x4f869c":"",
"0x4f8e7c":"",
"0x4f953c":"",
"0x4f9a18":"",
"0x4f9f34":"",
"0x4fa5ac":"",
"0x4fab64":"",
"0x4fb270":"",
"0x4fb9dc":"",
"0x4fc15c":"",
"0x4fc734":"",
"0x4fcea4":"",
"0x4fd5a4":"",
"0x4fdc70":"",
"0x4fe468":"",
"0x4fe994":"",
"0x4fee70":"",
"0x4ff68c":"",
"0x4ffbd0":"",
"0x50013c":"",
"0x5006a8":"",
"0x500b0c":"",
"0x501048":"",
"0x5017c0":"",
"0x501d78":"",
"0x5028f0":"",
"0x502d34":"",
"0x5033e4":"",
"0x503950":"",
"0x503ef4":"",
"0x5045b0":"",
"0x504cd4":"",
"0x505118":"",
"0x5055e8":"",
"0x505a2c":"",
"0x505ee4":"",
"0x6ebc28":"",
"0x6ec1e8":"",
"0x6ed4bc":"",
"0x6e6bc4":"",
"0x6e705c":"",
"0x6e7464":"",
"0x6e77f0":"",
"0x6e7a0c":"",
"0x6edf54":"",
"0x6ee66c":"",
"0x6eebe4":"",
"0x6eed78":"",
"0x7ec1d0":"",
"0x6e2710":"",
"0x6efd54":"",
"0x7f530c":"",
"0x7f54dc":"",
"0x6f3d5c":"",
"0x6f3fbc":"",
"0x6f4604":"",
"0x6f46b0":"",
"0x6f4888":"",
"0x6f4b58":"",
"0x7ebaa4":"",
"0x6f9bb8":"",
"0x6f9da0":"",
"0x6fd698":"",
"0x6fdcd0":"",
"0x6fa65c":"",
"0x6fa72c":"",
"0x6fcea4":"",
"0x6fd024":"",
"0x6f85fc":"",
"0x7e0df8":"",
"0x7e3a40":"",
"0x7e172c":"",
"0x7e469c":"",
"0x7e4ac8":"",
"0x7e5eec":"",
"0x7e68b4":"",
"0x7ec888":"",
"0x6f9624":"",
"0x6fbb08":"",
"0x6fc4a0":"",
"0x6fc358":"",
"0x6e0d28":"",
"0x7e6efc":"",
"0x7e71e0":"",
"0x7e7578":""
}

# ファルザー版の各種アドレス
RXX_Addr_List = [
["Map",      "0x6ED62C", "0x6EDCD6"],
["ChipText", "0x70E40E", "0x712342"],
["Enemy",    "0x71309E", "0x7136DF"],
["Navi",     "0x713850", "0x713C1F"],
["KeyItem",  "0x761160", "0x761446"],
["NaviCus",  "0x762005", "0x76216C"]
]

RXX_Sprite_Table = {
"startAddr":0x032CA8,
"endAddr":0x033963
}

def encodeByEXE6Dict(data):
    u""" バイナリ文字列をエグゼ６のテキストとしてエンコード
    """

    readPos = 0 # 読み取るアドレス
    L = []  # 出力するデータの配列

    while readPos < len(data):
        currentChar = data[readPos]

        if currentChar == "\xE4":
            u""" ２バイト文字フラグ
            """
            readPos += 1  # 次の文字を
            L.append( CP_EXE6_2[ data[readPos] ] )  # 2バイト文字として出力

        elif currentChar in ["\xF0", "\xF1", "\xF5"]:
            u""" 次の2バイトを使うコマンド
            """

            #L.append("\n" + hex(readPos) + ": ")
            #L.append("\n\n## ")
            L.append(CP_EXE6_1[currentChar])
            L.append( "[0x" + binascii.hexlify(data[readPos+1:readPos+1+2]) + "]")    # 文字コードの値をそのまま文字列として出力（'\xAB' -> "AB"）
            L.append("\n")

            readPos += 2

        elif currentChar in ["\xEE"]:
            u""" 次の3バイトを使うコマンド
            """
            L.append(CP_EXE6_1[currentChar])
            L.append( "[0x" + binascii.hexlify(data[readPos+1:readPos+1+3]) + "]")
            L.append("\n")

            readPos += 3

        # \xE6 リスト要素の終わりに現れるようなので、\xE6が現れたら次の要素の先頭アドレスを確認できるようにする
        elif currentChar == "\xE6":
            L.append(CP_EXE6_1[currentChar])
            #L.append("\n" + hex(readPos+1) + ": ")
            L.append("\n\n@ "  + hex(readPos+1) + " @\n")

        # テキストボックスを開く\xE8の次の1バイトは\0x00，\xE7も同様？
        elif currentChar in ["\xE7", "\xE8"]:
            #L.append("\n\n---\n")
            L.append(CP_EXE6_1[currentChar])
            readPos += 1
            L.append( "[0x" + binascii.hexlify(data[readPos]) + "]")
            if currentChar in ["\xE7"]:
                L.append("\n")
            elif currentChar in ["\xE8"]:
                L.append("\n")

        elif currentChar in ["\xE9", "\xF2"]:
            u""" 改行，テキストウインドウのクリア
            """
            L.append(CP_EXE6_1[ currentChar])
            L.append("\n")

        # 1バイト文字
        else:
            L.append( CP_EXE6_1[ currentChar ] )

        readPos += 1

        if readPos % 10000 == 0:    # 進捗表示
            sys.stdout.write(".")

    result = "".join(L)    # 配列を一つの文字列に連結
    return result


def decodeByEXE6Dict(string):
    u""" エグゼ６のテキストをバイナリ文字列にデコード
    """

    result = ""
    readPos = 0

    while readPos < len(string):
        currentChar = string[readPos].encode('utf-8')   # Unicode文字列から1文字取り出してString型に変換

        if currentChar == "@":
            u""" コメントは@で囲んでいる
            """
            #print "detect @ " + str(readPos)
            readPos += 1
            while string[readPos] != "@":
                readPos += 1
            #print "close @ " + str(readPos)
            readPos += 1
            continue

        # BXなどは(BX)と表記している
        if currentChar == "(":
            readPos += 1
            while string[readPos] != ")":
                currentChar += string[readPos]
                readPos += 1
            currentChar += string[readPos]

        # 改行などは<改行>などのコマンドとして表示している
        if currentChar == "<":
            readPos += 1
            while string[readPos] != ">":
                currentChar += string[readPos]
                readPos += 1
            currentChar += string[readPos]
            result += binascii.unhexlify(currentChar[1:3]) # <F5:顔>のF5だけ取り出して数値に戻す
            readPos += 1
            continue

        # 値は[0037]などのパラメータとして表示している
        if currentChar == "[":
            readPos += 1
            while string[readPos] != "]":
                currentChar += string[readPos]
                readPos += 1
            currentChar += string[readPos]
            result += binascii.unhexlify(currentChar[3:-1]) # [0xHHHH]のHHHHだけ取り出して数値に戻す
            readPos += 1
            continue

        if currentChar in CP_EXE6_2_inv:    # 2バイト文字なら
            result += "\xE4" + CP_EXE6_2_inv[currentChar]
        elif currentChar in CP_EXE6_1_inv:  # 1バイト文字なら
            result += CP_EXE6_1_inv[currentChar]
        else:   # 辞書に存在しない文字なら
            result += "\x80"    # ■に置き換え
            print u"辞書に「" + currentChar + "」と一致する文字がありません"

        readPos += 1

    return result
