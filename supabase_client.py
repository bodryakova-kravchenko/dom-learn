import os
import logging
from supabase import create_client, Client
from typing import List, Dict, Any, Optional, Union
from datetime import datetime

logger = logging.getLogger(__name__)

class SupabaseClient:
    def __init__(self):
        """Initialize Supabase client with environment variables."""
        self.url = os.environ.get("SUPABASE_URL")
        self.key = os.environ.get("SUPABASE_ANON_KEY")
        self.service_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        self.client: Optional[Client] = None
        self._ensure_connection()

    def _ensure_connection(self):
        """Establish connection to Supabase."""
        if not self.url or not self.key:
            logger.error("Missing Supabase URL or API key in environment variables")
            return
            
        try:
            # Use service key for full access if available
            self.client = create_client(self.url, self.service_key or self.key)
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            self.client = None

    def is_connected(self) -> bool:
        """Check if the client is connected to Supabase."""
        if not self.client:
            return False
        try:
            # Simple query to check connection
            self.client.table('levels').select('*').limit(1).execute()
            return True
        except Exception as e:
            logger.error(f"Connection check failed: {e}")
            return False

    # ===== LEVELS =====
    def get_all_levels(self) -> List[Dict[str, Any]]:
        """Get all levels ordered by order_index."""
        if not self.client:
            return []
        try:
            response = self.client.table('levels')\
                .select('*')\
                .order('order_index')\
                .execute()
            return response.data
        except Exception as e:
            logger.error(f"Error fetching levels: {e}")
            return []

    def create_level(self, title: str, order_index: int) -> Optional[Dict[str, Any]]:
        """Create a new level."""
        if not self.client:
            return None
        try:
            response = self.client.table('levels')\
                .insert({
                    'title': title,
                    'order_index': order_index
                })\
                .execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating level: {e}")
            return None

    def update_level(self, level_id: int, title: str) -> Optional[Dict[str, Any]]:
        """Update an existing level."""
        if not self.client:
            return None
        try:
            response = self.client.table('levels')\
                .update({
                    'title': title,
                    'updated_at': datetime.utcnow().isoformat()
                })\
                .eq('id', level_id)\
                .execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error updating level: {e}")
            return None

    def delete_level(self, level_id: int) -> bool:
        """Delete a level by ID."""
        if not self.client:
            return False
        try:
            response = self.client.table('levels')\
                .delete()\
                .eq('id', level_id)\
                .execute()
            return True
        except Exception as e:
            logger.error(f"Error deleting level: {e}")
            return False

    # ===== SECTIONS =====
    def get_sections_by_level(self, level_id: int) -> List[Dict[str, Any]]:
        """Get all sections for a specific level."""
        if not self.client:
            return []
        try:
            response = self.client.table('sections')\
                .select('*')\
                .eq('level_id', level_id)\
                .order('order_index')\
                .execute()
            return response.data
        except Exception as e:
            logger.error(f"Error fetching sections: {e}")
            return []

    def create_section(self, level_id: int, title: str, order_index: int) -> Optional[Dict[str, Any]]:
        """Create a new section in a level."""
        if not self.client:
            return None
        try:
            response = self.client.table('sections')\
                .insert({
                    'level_id': level_id,
                    'title': title,
                    'order_index': order_index
                })\
                .execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating section: {e}")
            return None
            
    def update_section(self, section_id: int, title: str) -> Optional[Dict[str, Any]]:
        """Update an existing section."""
        if not self.client:
            return None
        try:
            response = self.client.table('sections')\
                .update({
                    'title': title,
                    'updated_at': datetime.utcnow().isoformat()
                })\
                .eq('id', section_id)\
                .execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error updating section: {e}")
            return None
            
    def delete_section(self, section_id: int) -> bool:
        """Delete a section by ID.
        
        Args:
            section_id: The ID of the section to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        if not self.client:
            return False
            
        try:
            response = self.client.table('sections')\
                .delete()\
                .eq('id', section_id)\
                .execute()
                
            # Return True if any rows were affected
            return bool(response.data and len(response.data) > 0)
            
        except Exception as e:
            logger.error(f"Error deleting section {section_id}: {e}")
            return False

    # ===== LESSONS =====
    def get_lessons_by_section(self, section_id: int) -> List[Dict[str, Any]]:
        """Get all lessons for a specific section."""
        if not self.client:
            return []
        try:
            response = self.client.table('lessons')\
                .select('*')\
                .eq('section_id', section_id)\
                .order('order_index')\
                .execute()
            return response.data
        except Exception as e:
            logger.error(f"Error fetching lessons: {e}")
            return []

    def create_lesson(self, section_id: int, title: str, order_index: int, 
                     content: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """Create a new lesson in a section."""
        if not self.client:
            return None
        try:
            data = {
                'section_id': section_id,
                'title': title,
                'order_index': order_index
            }
            if content is not None:
                data['content'] = content
                
            response = self.client.table('lessons')\
                .insert(data)\
                .execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating lesson: {e}")
            return None

    def get_lesson_by_id(self, lesson_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific lesson by ID."""
        if not self.client:
            return None
        try:
            response = self.client.table('lessons')\
                .select('*')\
                .eq('id', lesson_id)\
                .single()\
                .execute()
            return response.data if response.data else None
        except Exception as e:
            logger.error(f"Error fetching lesson {lesson_id}: {e}")
            return None
            
    def update_lesson(self, lesson_id: int, title: str, content: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing lesson.
        
        Args:
            lesson_id: The ID of the lesson to update
            title: New title for the lesson
            content: Dictionary containing lesson content (theory, quiz, tasks)
            
        Returns:
            Updated lesson data if successful, None otherwise
        """
        if not self.client:
            return None
            
        try:
            update_data = {
                'title': title,
                'content': content,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            response = self.client.table('lessons')\
                .update(update_data)\
                .eq('id', lesson_id)\
                .execute()
                
            return response.data[0] if response.data else None
            
        except Exception as e:
            logger.error(f"Error updating lesson {lesson_id}: {e}")
            return None
            
    def delete_lesson(self, lesson_id: int) -> bool:
        """Delete a lesson by ID.
        
        Args:
            lesson_id: The ID of the lesson to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        if not self.client:
            return False
            
        try:
            response = self.client.table('lessons')\
                .delete()\
                .eq('id', lesson_id)\
                .execute()
                
            # Return True if any rows were affected
            return bool(response.data and len(response.data) > 0)
            
        except Exception as e:
            logger.error(f"Error deleting lesson {lesson_id}: {e}")
            return False

    # ===== FILE UPLOADS =====
    def upload_file(self, bucket_name: str, file_path: str, file_content: bytes, 
                   content_type: str = 'image/jpeg') -> Optional[str]:
        """Upload a file to Supabase storage."""
        if not self.client:
            return None
        try:
            # Ensure the bucket exists
            try:
                self.client.storage.get_bucket(bucket_name)
            except:
                self.client.storage.create_bucket(bucket_name, public=True)
            
            # Upload file
            response = self.client.storage.\
                from_('local').\
                upload(
                    path=file_path,
                    file=file_content,
                    file_options={"content-type": content_type}
                )
            
            # Get public URL
            result = self.client.storage.\
                from_('local').\
                get_public_url(file_path)
            
            return result.public_url if hasattr(result, 'public_url') else None
            
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            return None

# Global instance
supabase_client = SupabaseClient()
