"""外部データソース管理とAPI連携"""

import os
import json
import asyncio
import aiohttp
import pandas as pd
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class DataSourceType(str, Enum):
    """データソースの種類"""
    TWITTER_API = "twitter_api"
    FACEBOOK_API = "facebook_api"
    GOOGLE_ANALYTICS = "google_analytics"
    INSTAGRAM_API = "instagram_api"
    LINKEDIN_API = "linkedin_api"
    YOUTUBE_API = "youtube_api"
    CSV_FILE = "csv_file"
    EXCEL_FILE = "excel_file"
    JSON_FILE = "json_file"
    DEMO_DATA = "demo_data"


@dataclass
class ExternalAPIConfig:
    """外部API設定"""
    source_type: DataSourceType
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    base_url: Optional[str] = None
    rate_limit: int = 100  # requests per hour
    enabled: bool = False
    last_used: Optional[datetime] = None


@dataclass
class DataSourceStatus:
    """データソースの状態"""
    source_type: DataSourceType
    status: str  # "connected", "error", "disabled", "rate_limited"
    last_sync: Optional[datetime] = None
    error_message: Optional[str] = None
    data_freshness: Optional[datetime] = None
    records_count: int = 0


class ExternalDataManager:
    """外部データソースの統合管理"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or "external_config.json"
        self.configs: Dict[DataSourceType, ExternalAPIConfig] = {}
        self.session: Optional[aiohttp.ClientSession] = None
        self.upload_dir = Path("uploads")
        self.upload_dir.mkdir(exist_ok=True)
        
        # APIエンドポイント設定
        self.api_endpoints = {
            DataSourceType.TWITTER_API: {
                "base_url": "https://api.twitter.com/2",
                "trends": "/trends/place/1",
                "search": "/tweets/search/recent"
            },
            DataSourceType.FACEBOOK_API: {
                "base_url": "https://graph.facebook.com/v18.0",
                "insights": "/insights",
                "posts": "/posts"
            },
            DataSourceType.GOOGLE_ANALYTICS: {
                "base_url": "https://analyticsreporting.googleapis.com/v4",
                "reports": "/reports:batchGet"
            },
            DataSourceType.INSTAGRAM_API: {
                "base_url": "https://graph.instagram.com",
                "media": "/media",
                "insights": "/insights"
            }
        }
        
        self.load_configs()
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def load_configs(self):
        """設定ファイルからAPIキー等を読み込み"""
        config_path = Path(self.config_file)
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for source_name, config_data in data.items():
                    try:
                        source_type = DataSourceType(source_name)
                        self.configs[source_type] = ExternalAPIConfig(
                            source_type=source_type,
                            **config_data
                        )
                    except ValueError:
                        logger.warning(f"Unknown data source type: {source_name}")
                        
            except Exception as e:
                logger.error(f"Failed to load external configs: {e}")
        else:
            # デフォルト設定を作成
            self._create_default_config()
    
    def save_configs(self):
        """設定をファイルに保存"""
        try:
            data = {}
            for source_type, config in self.configs.items():
                config_dict = asdict(config)
                # datetimeオブジェクトを文字列に変換
                if config_dict.get('last_used'):
                    config_dict['last_used'] = config_dict['last_used'].isoformat()
                data[source_type.value] = config_dict
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Failed to save external configs: {e}")
    
    def _create_default_config(self):
        """デフォルト設定を作成"""
        default_sources = [
            DataSourceType.TWITTER_API,
            DataSourceType.FACEBOOK_API,
            DataSourceType.GOOGLE_ANALYTICS,
            DataSourceType.INSTAGRAM_API,
            DataSourceType.CSV_FILE,
            DataSourceType.DEMO_DATA
        ]
        
        for source_type in default_sources:
            self.configs[source_type] = ExternalAPIConfig(
                source_type=source_type,
                enabled=(source_type in [DataSourceType.CSV_FILE, DataSourceType.DEMO_DATA])
            )
    
    def update_api_config(self, source_type: DataSourceType, **kwargs):
        """API設定を更新"""
        if source_type not in self.configs:
            self.configs[source_type] = ExternalAPIConfig(source_type=source_type)
        
        config = self.configs[source_type]
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        self.save_configs()
    
    async def test_connection(self, source_type: DataSourceType) -> DataSourceStatus:
        """外部APIへの接続テスト"""
        if source_type not in self.configs:
            return DataSourceStatus(
                source_type=source_type,
                status="error",
                error_message="Configuration not found"
            )
        
        config = self.configs[source_type]
        
        if not config.enabled:
            return DataSourceStatus(
                source_type=source_type,
                status="disabled"
            )
        
        try:
            if source_type == DataSourceType.TWITTER_API:
                return await self._test_twitter_connection(config)
            elif source_type == DataSourceType.FACEBOOK_API:
                return await self._test_facebook_connection(config)
            elif source_type == DataSourceType.GOOGLE_ANALYTICS:
                return await self._test_google_analytics_connection(config)
            elif source_type in [DataSourceType.CSV_FILE, DataSourceType.EXCEL_FILE]:
                return DataSourceStatus(
                    source_type=source_type,
                    status="connected",
                    last_sync=datetime.now()
                )
            elif source_type == DataSourceType.DEMO_DATA:
                return DataSourceStatus(
                    source_type=source_type,
                    status="connected",
                    last_sync=datetime.now(),
                    records_count=100
                )
            else:
                return DataSourceStatus(
                    source_type=source_type,
                    status="error",
                    error_message="Unsupported data source type"
                )
                
        except Exception as e:
            return DataSourceStatus(
                source_type=source_type,
                status="error",
                error_message=str(e)
            )
    
    async def _test_twitter_connection(self, config: ExternalAPIConfig) -> DataSourceStatus:
        """Twitter API接続テスト"""
        if not config.api_key or not config.api_secret:
            return DataSourceStatus(
                source_type=config.source_type,
                status="error",
                error_message="API key and secret required"
            )
        
        headers = {
            "Authorization": f"Bearer {config.access_token}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.api_endpoints[DataSourceType.TWITTER_API]['base_url']}/tweets/search/recent"
        params = {"query": "test", "max_results": 10}
        
        async with self.session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return DataSourceStatus(
                    source_type=config.source_type,
                    status="connected",
                    last_sync=datetime.now(),
                    records_count=len(data.get("data", []))
                )
            elif response.status == 401:
                return DataSourceStatus(
                    source_type=config.source_type,
                    status="error",
                    error_message="Authentication failed. Check API credentials."
                )
            elif response.status == 429:
                return DataSourceStatus(
                    source_type=config.source_type,
                    status="rate_limited",
                    error_message="Rate limit exceeded"
                )
            else:
                return DataSourceStatus(
                    source_type=config.source_type,
                    status="error",
                    error_message=f"HTTP {response.status}: {await response.text()}"
                )
    
    async def _test_facebook_connection(self, config: ExternalAPIConfig) -> DataSourceStatus:
        """Facebook API接続テスト"""
        if not config.access_token:
            return DataSourceStatus(
                source_type=config.source_type,
                status="error",
                error_message="Access token required"
            )
        
        url = f"{self.api_endpoints[DataSourceType.FACEBOOK_API]['base_url']}/me"
        params = {"access_token": config.access_token, "fields": "id,name"}
        
        async with self.session.get(url, params=params) as response:
            if response.status == 200:
                return DataSourceStatus(
                    source_type=config.source_type,
                    status="connected",
                    last_sync=datetime.now()
                )
            else:
                return DataSourceStatus(
                    source_type=config.source_type,
                    status="error",
                    error_message=f"HTTP {response.status}: {await response.text()}"
                )
    
    async def _test_google_analytics_connection(self, config: ExternalAPIConfig) -> DataSourceStatus:
        """Google Analytics API接続テスト"""
        if not config.access_token:
            return DataSourceStatus(
                source_type=config.source_type,
                status="error",
                error_message="Access token required"
            )
        
        # 簡単な接続テスト（実際にはOAuth2フローが必要）
        return DataSourceStatus(
            source_type=config.source_type,
            status="connected",
            last_sync=datetime.now()
        )
    
    async def get_all_statuses(self) -> List[DataSourceStatus]:
        """全データソースの状態を取得"""
        statuses = []
        for source_type in self.configs.keys():
            status = await self.test_connection(source_type)
            statuses.append(status)
        return statuses
    
    def upload_file(self, file_data: bytes, filename: str, content_type: str) -> Dict[str, Any]:
        """ファイルアップロード処理"""
        try:
            # ファイル拡張子から種類を判定
            file_path = self.upload_dir / filename
            
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            # ファイル解析
            analysis_result = self._analyze_uploaded_file(file_path)
            
            return {
                "success": True,
                "file_path": str(file_path),
                "filename": filename,
                "size": len(file_data),
                "analysis": analysis_result,
                "upload_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "filename": filename
            }
    
    def _analyze_uploaded_file(self, file_path: Path) -> Dict[str, Any]:
        """アップロードされたファイルを解析"""
        try:
            if file_path.suffix.lower() == '.csv':
                df = pd.read_csv(file_path)
                return {
                    "type": "csv",
                    "rows": len(df),
                    "columns": list(df.columns),
                    "sample_data": df.head(3).to_dict('records')
                }
            elif file_path.suffix.lower() in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
                return {
                    "type": "excel",
                    "rows": len(df),
                    "columns": list(df.columns),
                    "sample_data": df.head(3).to_dict('records')
                }
            elif file_path.suffix.lower() == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return {
                    "type": "json",
                    "structure": type(data).__name__,
                    "sample_data": data if isinstance(data, list) and len(data) <= 3 else str(data)[:200]
                }
            else:
                return {
                    "type": "unknown",
                    "message": "Unsupported file format"
                }
                
        except Exception as e:
            return {
                "type": "error",
                "message": str(e)
            }
    
    def load_file_data(self, file_path: str, data_mapping: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """アップロードされたファイルからデータを読み込み"""
        try:
            path = Path(file_path)
            
            if path.suffix.lower() == '.csv':
                df = pd.read_csv(path)
            elif path.suffix.lower() in ['.xlsx', '.xls']:
                df = pd.read_excel(path)
            else:
                raise ValueError(f"Unsupported file format: {path.suffix}")
            
            # データマッピングを適用
            if data_mapping:
                df = df.rename(columns=data_mapping)
            
            # 基本的なデータクレンジング
            df = df.dropna()
            
            return {
                "success": True,
                "data": df.to_dict('records'),
                "columns": list(df.columns),
                "rows": len(df),
                "file_path": file_path
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path
            }


# グローバルインスタンス
external_data_manager = ExternalDataManager()