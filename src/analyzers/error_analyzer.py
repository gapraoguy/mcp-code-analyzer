"""
Python error analysis and basic fix suggestions
"""
import re
from typing import Tuple


class ErrorAnalyzer:
    """Python固有のエラー解析と基本的な修正提案"""
    
    @staticmethod
    def analyze_error(error_message: str, file_path: str = None) -> Tuple[str, str]:
        """
        Pythonエラーメッセージを解析して基本的な修正提案を生成
        
        Args:
            error_message: エラーメッセージ
            file_path: エラーが発生したファイルパス（オプション）
            
        Returns:
            tuple: (提案テキスト, 修正コード例)
        """
        error_lower = error_message.lower()
        
        # SyntaxError の解析
        if "syntaxerror" in error_lower:
            return ErrorAnalyzer._analyze_syntax_error(error_message)
        
        # NameError の解析
        elif "nameerror" in error_lower:
            return ErrorAnalyzer._analyze_name_error(error_message)
        
        # TypeError の解析
        elif "typeerror" in error_lower:
            return ErrorAnalyzer._analyze_type_error(error_message)
        
        # ImportError / ModuleNotFoundError の解析
        elif any(err in error_lower for err in ["importerror", "modulenotfounderror"]):
            return ErrorAnalyzer._analyze_import_error(error_message)
        
        # IndentationError の解析
        elif "indentationerror" in error_lower:
            return ErrorAnalyzer._analyze_indentation_error(error_message)
        
        # AttributeError の解析
        elif "attributeerror" in error_lower:
            return ErrorAnalyzer._analyze_attribute_error(error_message)
        
        # KeyError の解析
        elif "keyerror" in error_lower:
            return ErrorAnalyzer._analyze_key_error(error_message)
        
        # IndexError の解析
        elif "indexerror" in error_lower:
            return ErrorAnalyzer._analyze_index_error(error_message)
        
        # 汎用エラー
        else:
            return ErrorAnalyzer._analyze_generic_error(error_message)
    
    @staticmethod
    def _analyze_syntax_error(error_message: str) -> Tuple[str, str]:
        """SyntaxError の解析"""
        if "invalid syntax" in error_message:
            return (
                "Python構文エラーが検出されました。コロン、括弧、インデントの問題を確認してください。",
                "# よくある修正例:\n"
                "# 1. if文の後にコロンを追加: if condition:\n"
                "# 2. 括弧の対応を確認: print(\"hello\")\n"
                "# 3. インデントの確認（4スペース推奨）"
            )
        elif "eof while scanning" in error_message:
            return (
                "文字列または括弧が閉じられていません。",
                "# 修正例:\n"
                "# 1. 文字列を閉じる: \"text\"\n"
                "# 2. 括弧を閉じる: (expression)\n"
                "# 3. 辞書を閉じる: {\"key\": \"value\"}"
            )
        else:
            return (
                "Python構文エラーです。エラー位置の構文を確認してください。",
                "# 構文エラーの一般的な確認点:\n"
                "# - コロン (:) の追加\n"
                "# - 括弧の対応\n"
                "# - 引用符の対応"
            )
    
    @staticmethod
    def _analyze_name_error(error_message: str) -> Tuple[str, str]:
        """NameError の解析"""
        # 変数名を抽出
        match = re.search(r"name '(\w+)' is not defined", error_message)
        var_name = match.group(1) if match else "variable"
        
        return (
            f"未定義の変数 '{var_name}' が使用されています。",
            f"# 修正例:\n"
            f"# 1. 変数を定義: {var_name} = ...\n"
            f"# 2. インポート: from module import {var_name}\n"
            f"# 3. スペルミスの確認"
        )
    
    @staticmethod
    def _analyze_type_error(error_message: str) -> Tuple[str, str]:
        """TypeError の解析"""
        if "missing" in error_message and "argument" in error_message:
            return (
                "関数の引数が不足しています。",
                "# 修正例:\n"
                "# function(arg1, arg2)  # 必要な引数を追加\n"
                "# または関数定義にデフォルト値を設定"
            )
        elif "too many" in error_message and "argument" in error_message:
            return (
                "関数の引数が多すぎます。",
                "# 修正例:\n"
                "# 余分な引数を削除\n"
                "# または関数定義で *args を使用"
            )
        elif "unsupported operand" in error_message:
            return (
                "サポートされていない演算子の使用です。データ型を確認してください。",
                "# 修正例:\n"
                "# str(number) + string  # 型変換\n"
                "# int(string) + number  # 型変換"
            )
        else:
            return (
                "型エラーです。データ型と関数の使用方法を確認してください。",
                "# 修正例:\n"
                "# - 引数の型を確認\n"
                "# - 必要に応じて型変換\n"
                "# - 関数のシグネチャを確認"
            )
    
    @staticmethod
    def _analyze_import_error(error_message: str) -> Tuple[str, str]:
        """ImportError / ModuleNotFoundError の解析"""
        # モジュール名を抽出
        match = re.search(r"No module named '([^']+)'", error_message)
        module_name = match.group(1) if match else "module"
        
        return (
            f"モジュール '{module_name}' が見つかりません。",
            f"# 修正例:\n"
            f"# 1. パッケージをインストール: pip install {module_name}\n"
            f"# 2. インポートパスを確認\n"
            f"# 3. 仮想環境の有効化を確認"
        )
    
    @staticmethod
    def _analyze_indentation_error(error_message: str) -> Tuple[str, str]:
        """IndentationError の解析"""
        return (
            "Pythonインデントエラーです。一貫したインデントを使用してください。",
            "# 修正例:\n"
            "# 1. 4スペースの一貫したインデント使用\n"
            "# 2. タブとスペースを混在させない\n"
            "# 3. コードブロックの適切なネスト"
        )
    
    @staticmethod
    def _analyze_attribute_error(error_message: str) -> Tuple[str, str]:
        """AttributeError の解析"""
        # 属性名を抽出
        match = re.search(r"'(\w+)' object has no attribute '(\w+)'", error_message)
        if match:
            obj_type, attr_name = match.groups()
            return (
                f"'{obj_type}' オブジェクトに '{attr_name}' 属性がありません。",
                f"# 修正例:\n"
                f"# 1. 属性名のスペルを確認\n"
                f"# 2. オブジェクトの型を確認\n"
                f"# 3. dir({obj_type.lower()}_obj) で利用可能な属性を確認"
            )
        else:
            return (
                "属性エラーです。オブジェクトの属性を確認してください。",
                "# 修正例:\n"
                "# - 属性名のスペル確認\n"
                "# - オブジェクトの型確認\n"
                "# - dir(object) で属性一覧確認"
            )
    
    @staticmethod
    def _analyze_key_error(error_message: str) -> Tuple[str, str]:
        """KeyError の解析"""
        match = re.search(r"KeyError: '([^']+)'", error_message)
        key_name = match.group(1) if match else "key"
        
        return (
            f"辞書にキー '{key_name}' が存在しません。",
            f"# 修正例:\n"
            f"# 1. dict.get('{key_name}', default_value)  # 安全な取得\n"
            f"# 2. if '{key_name}' in dict:  # 存在確認\n"
            f"# 3. キー名のスペル確認"
        )
    
    @staticmethod
    def _analyze_index_error(error_message: str) -> Tuple[str, str]:
        """IndexError の解析"""
        return (
            "リストのインデックスが範囲外です。",
            "# 修正例:\n"
            "# 1. if index < len(list):  # インデックス範囲確認\n"
            "# 2. try-except IndexError:  # 例外処理\n"
            "# 3. リストの長さを確認"
        )
    
    @staticmethod
    def _analyze_generic_error(error_message: str) -> Tuple[str, str]:
        """汎用エラー解析"""
        return (
            f"Python実行エラー: {error_message}",
            "# 一般的な確認点:\n"
            "# 1. エラーメッセージを詳しく読む\n"
            "# 2. 該当行番号を確認\n"
            "# 3. Python公式ドキュメントを参照"
        )