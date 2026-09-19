"""
📄 Content Command Handlers - Content Management and Processing

Command handlers for content-related operations extracted from monolithic mova.py
with enhanced functionality for content processing and management.
"""

import json
import os
import hashlib
from typing import Any, Dict, Optional, List
from datetime import datetime
from pathlib import Path

from ..cli.utils import make_request, detect_service_name


def handle_content_command(args: Any) -> bool:
    """
    Handle content management command

    Args:
        args: Parsed command arguments

    Returns:
        True if successful
    """
    try:
        action = getattr(args, 'content_action', None)

        if action == 'list':
            return _handle_content_list(args)
        elif action == 'add':
            return _handle_content_add(args)
        elif action == 'remove':
            return _handle_content_remove(args)
        elif action == 'search':
            return _handle_content_search(args)
        elif action == 'info':
            return _handle_content_info(args)
        else:
            print(f"❌ Unknown content action: {action}")
            print("💡 Available actions: list, add, remove, search, info")
            return False

    except Exception as e:
        print(f"❌ Content command error: {e}")
        return False


def handle_upload_command(args: Any) -> bool:
    """
    Handle file upload command

    Args:
        args: Parsed command arguments

    Returns:
        True if successful
    """
    try:
        file_path = args.file_path
        content_type = getattr(args, 'type', 'auto')
        description = getattr(args, 'description', '')

        print(f"📤 Uploading file: {file_path}")

        # Validate file exists
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return False

        # Get file info
        file_size = os.path.getsize(file_path)
        file_name = os.path.basename(file_path)

        print(f"📄 File: {file_name}")
        print(f"📊 Size: {file_size} bytes")
        print(f"🏷️ Type: {content_type}")

        # Calculate file hash
        file_hash = _calculate_file_hash(file_path)

        # Prepare upload data
        upload_data = {
            'file_name': file_name,
            'file_size': file_size,
            'file_hash': file_hash,
            'content_type': content_type,
            'description': description,
            'service': detect_service_name(),
            'timestamp': datetime.now().isoformat()
        }

        # Read file content
        try:
            with open(file_path, 'rb') as f:
                file_content = f.read()
        except Exception as e:
            print(f"❌ Failed to read file: {e}")
            return False

        # Send upload request
        response = make_request("POST", "/api/content/upload", upload_data,
                              files={'file': file_content}, server=args.server)

        if response.get('success', False):
            print("✅ File uploaded successfully")

            if 'content_id' in response:
                print(f"🆔 Content ID: {response['content_id']}")

            if 'url' in response:
                print(f"🔗 URL: {response['url']}")

            return True
        else:
            print("❌ Failed to upload file")
            if 'error' in response:
                print(f"💥 Error: {response['error']}")
            return False

    except Exception as e:
        print(f"❌ Upload error: {e}")
        return False


def handle_download_command(args: Any) -> bool:
    """
    Handle file download command

    Args:
        args: Parsed command arguments

    Returns:
        True if successful
    """
    try:
        content_id = args.content_id
        output_path = getattr(args, 'output', None)

        print(f"📥 Downloading content: {content_id}")

        # Get content info first
        response = make_request("GET", f"/api/content/{content_id}/info", server=args.server)

        if not response.get('success', False):
            print("❌ Content not found")
            return False

        content_info = response.get('content', {})
        file_name = content_info.get('file_name', f'download_{content_id}')

        # Determine output path
        if not output_path:
            output_path = file_name
        elif os.path.isdir(output_path):
            output_path = os.path.join(output_path, file_name)

        print(f"💾 Output: {output_path}")

        # Download content
        download_response = make_request("GET", f"/api/content/{content_id}/download", server=args.server)

        if download_response.get('success', False):
            file_content = download_response.get('content', b'')

            # Save file
            try:
                with open(output_path, 'wb') as f:
                    f.write(file_content)

                print("✅ File downloaded successfully")
                print(f"📁 Saved to: {output_path}")
                return True
            except Exception as e:
                print(f"❌ Failed to save file: {e}")
                return False
        else:
            print("❌ Failed to download content")
            if 'error' in download_response:
                print(f"💥 Error: {download_response['error']}")
            return False

    except Exception as e:
        print(f"❌ Download error: {e}")
        return False


def _handle_content_list(args: Any) -> bool:
    """Handle content listing"""
    try:
        detailed = getattr(args, 'detailed', False)
        content_type = getattr(args, 'type', None)
        limit = getattr(args, 'limit', 50)

        print("📋 Content List")
        print("-" * 20)

        params = {'limit': limit}
        if content_type:
            params['type'] = content_type

        response = make_request("GET", "/api/content", params, server=args.server)
        content_list = response.get('content', [])

        if not content_list:
            print("📭 No content found")
            return True

        for i, content in enumerate(content_list, 1):
            content_id = content.get('id', 'Unknown')
            name = content.get('file_name', 'Unknown')
            size = content.get('file_size', 0)
            upload_date = content.get('upload_date', 'Unknown')

            print(f"{i}. 📄 {name}")

            if detailed:
                print(f"   ID: {content_id}")
                print(f"   Size: {_format_file_size(size)}")
                print(f"   Type: {content.get('content_type', 'Unknown')}")
                print(f"   Uploaded: {upload_date}")

                if content.get('description'):
                    print(f"   Description: {content['description']}")

                print()
            else:
                print(f"   ID: {content_id} | Size: {_format_file_size(size)}")

        total = response.get('total', len(content_list))
        if total > len(content_list):
            print(f"\n📊 Showing {len(content_list)} of {total} items")

        return True

    except Exception as e:
        print(f"❌ Content list error: {e}")
        return False


def _handle_content_add(args: Any) -> bool:
    """Handle content addition via URL or text"""
    try:
        source = args.source
        content_type = getattr(args, 'type', 'auto')
        title = getattr(args, 'title', '')
        description = getattr(args, 'description', '')

        print(f"➕ Adding content from: {source}")

        # Prepare content data
        content_data = {
            'source': source,
            'content_type': content_type,
            'title': title,
            'description': description,
            'service': detect_service_name(),
            'timestamp': datetime.now().isoformat()
        }

        response = make_request("POST", "/api/content/add", content_data, server=args.server)

        if response.get('success', False):
            print("✅ Content added successfully")

            if 'content_id' in response:
                print(f"🆔 Content ID: {response['content_id']}")

            if 'processed' in response:
                processed = response['processed']
                print(f"📊 Processed: {processed.get('words', 0)} words, {processed.get('size', 0)} bytes")

            return True
        else:
            print("❌ Failed to add content")
            if 'error' in response:
                print(f"💥 Error: {response['error']}")
            return False

    except Exception as e:
        print(f"❌ Content add error: {e}")
        return False


def _handle_content_remove(args: Any) -> bool:
    """Handle content removal"""
    try:
        content_id = args.content_id

        print(f"🗑️ Removing content: {content_id}")

        # Confirm deletion if not forced
        force = getattr(args, 'force', False)
        if not force:
            confirm = input("Are you sure you want to delete this content? (y/N): ")
            if confirm.lower() != 'y':
                print("❌ Deletion cancelled")
                return False

        remove_data = {
            'content_id': content_id,
            'service': detect_service_name(),
            'timestamp': datetime.now().isoformat()
        }

        response = make_request("DELETE", f"/api/content/{content_id}", remove_data, server=args.server)

        if response.get('success', False):
            print("✅ Content removed successfully")
            return True
        else:
            print("❌ Failed to remove content")
            if 'error' in response:
                print(f"💥 Error: {response['error']}")
            return False

    except Exception as e:
        print(f"❌ Content remove error: {e}")
        return False


def _handle_content_search(args: Any) -> bool:
    """Handle content search"""
    try:
        query = args.query
        content_type = getattr(args, 'type', None)
        limit = getattr(args, 'limit', 20)

        print(f"🔍 Searching content: {query}")

        search_params = {
            'query': query,
            'limit': limit
        }

        if content_type:
            search_params['type'] = content_type

        response = make_request("GET", "/api/content/search", search_params, server=args.server)
        results = response.get('results', [])

        if not results:
            print("📭 No matching content found")
            return True

        print(f"📊 Found {len(results)} results:")
        print("-" * 30)

        for i, result in enumerate(results, 1):
            title = result.get('title', result.get('file_name', 'Untitled'))
            score = result.get('score', 0)
            snippet = result.get('snippet', '')
            content_id = result.get('id', 'Unknown')

            print(f"{i}. 📄 {title}")
            print(f"   ID: {content_id} | Score: {score:.2f}")

            if snippet:
                print(f"   Preview: {snippet[:100]}...")

            print()

        return True

    except Exception as e:
        print(f"❌ Content search error: {e}")
        return False


def _handle_content_info(args: Any) -> bool:
    """Handle content information display"""
    try:
        content_id = args.content_id

        print(f"ℹ️ Content Information: {content_id}")
        print("-" * 35)

        response = make_request("GET", f"/api/content/{content_id}/info", server=args.server)

        if not response.get('success', False):
            print("❌ Content not found")
            return False

        content = response.get('content', {})

        # Basic info
        print(f"📄 Name: {content.get('file_name', 'Unknown')}")
        print(f"🆔 ID: {content.get('id', 'Unknown')}")
        print(f"📊 Size: {_format_file_size(content.get('file_size', 0))}")
        print(f"🏷️ Type: {content.get('content_type', 'Unknown')}")
        print(f"📅 Uploaded: {content.get('upload_date', 'Unknown')}")

        if content.get('description'):
            print(f"📝 Description: {content['description']}")

        # Hash and verification
        if content.get('file_hash'):
            print(f"🔐 Hash: {content['file_hash']}")

        # Processing info
        if content.get('processed'):
            processed = content['processed']
            print(f"⚙️ Processing:")
            print(f"   Words: {processed.get('words', 0)}")
            print(f"   Lines: {processed.get('lines', 0)}")
            print(f"   Language: {processed.get('language', 'Unknown')}")

        # Access info
        if content.get('access_count'):
            print(f"👁️ Access count: {content['access_count']}")

        if content.get('last_accessed'):
            print(f"🕐 Last accessed: {content['last_accessed']}")

        return True

    except Exception as e:
        print(f"❌ Content info error: {e}")
        return False


def _calculate_file_hash(file_path: str) -> str:
    """Calculate SHA-256 hash of file"""
    try:
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    except Exception:
        return ""


def _format_file_size(size: int) -> str:
    """Format file size in human readable format"""
    if size == 0:
        return "0 B"

    units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0

    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1

    if unit_index == 0:
        return f"{size} {units[unit_index]}"
    else:
        return f"{size:.2f} {units[unit_index]}"
