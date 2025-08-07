import os
import json
import time
import uuid
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

def list_supabase_tables(supabase: Client):
    """List all tables in the Supabase database."""
    print("\n🔍 Listing database tables...")
    
    try:
        # Try to get the list of tables from the information_schema
        response = supabase.rpc('get_tables', {}).execute()
        
        if hasattr(response, 'data') and isinstance(response.data, list):
            tables = response.data
            print(f"✅ Found {len(tables)} tables in the database:")
            for i, table in enumerate(tables, 1):
                print(f"  {i}. {table.get('table_name', 'unknown')}")
            return tables
        else:
            print("❌ Could not retrieve table list. Trying alternative method...")
            
            # Alternative method: Try to query information_schema directly
            try:
                response = supabase.from_('information_schema.tables') \
                    .select('table_name') \
                    .eq('table_schema', 'public') \
                    .execute()
                
                if hasattr(response, 'data') and isinstance(response.data, list):
                    tables = [t['table_name'] for t in response.data]
                    print(f"✅ Found {len(tables)} tables in the database:")
                    for i, table_name in enumerate(tables, 1):
                        print(f"  {i}. {table_name}")
                    return tables
                else:
                    print("❌ Could not retrieve table list using information_schema")
                    return []
                    
            except Exception as e:
                print(f"❌ Error querying information_schema: {str(e)}")
                return []
    
    except Exception as e:
        print(f"❌ Error listing tables: {str(e)}")
        return []

def test_database_operations(supabase: Client):
    """Test basic database operations by trying to access potential tables."""
    # List of potential tables that might exist in the application
    potential_tables = [
        'lessons', 'lesson', 'courses', 'course', 
        'users', 'user', 'content', 'pages', 'modules'
    ]
    
    print("\n🔍 Testing direct table access...")
    
    for table_name in potential_tables:
        try:
            print(f"  Trying to access table: {table_name}")
            
            # Try to get a single record from the table
            response = supabase.table(table_name).select("*").limit(1).execute()
            
            if hasattr(response, 'data') and isinstance(response.data, list):
                print(f"  ✅ Successfully accessed table: {table_name}")
                print(f"  Found {len(response.data)} records")
                
                if response.data:
                    print("  First record columns:", ", ".join(response.data[0].keys()))
                
                # Try to get record count
                try:
                    count_response = supabase.table(table_name).select("*", count='exact').execute()
                    if hasattr(count_response, 'count'):
                        print(f"  Total records in {table_name}: {count_response.count}")
                except Exception as e:
                    print(f"  Could not get record count: {str(e)}")
                
                return True
                
        except Exception as e:
            if 'permission denied' in str(e).lower():
                print(f"  ❌ Permission denied for table: {table_name}")
            elif 'relation "public.' in str(e).lower():
                # Table doesn't exist, try the next one
                continue
            else:
                print(f"  ❌ Error accessing table {table_name}: {str(e)}")
    
    print("\n❌ Could not access any known tables.")
    print("ℹ️  Possible reasons:")
    print("  1. The tables might not exist in the database")
    print("  2. The user might not have permission to access the tables")
    print("  3. The table names might be different than expected")
    print("\nPlease check your Supabase dashboard to verify the table names and permissions.")
    return False

def test_supabase_connection():
    # Load environment variables from .env file
    load_dotenv()
    
    # Get Supabase credentials from environment variables
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Error: Missing Supabase URL or API key in .env file")
        return False
    
    print(f"Supabase URL: {supabase_url}")
    print("Testing connection...")
    
    try:
        # Initialize the Supabase client
        print("Initializing Supabase client...")
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Test 1: Check if we can connect to the Supabase client
        print("\n🔍 Testing basic client connection...")
        if not supabase or not hasattr(supabase, 'auth'):
            print("❌ Failed to initialize Supabase client")
            return False
        print("✅ Basic client connection successful")
        
        # Test 2: Try to access the auth endpoint (should be available with anon key)
        print("\n🔍 Testing auth endpoint access...")
        try:
            # This should work with just the anon key
            response = supabase.auth.get_user()
            
            # If we get here, the connection was successful, even if there's no user
            print("✅ Successfully connected to Supabase!")
            print("ℹ️  Note: This is an anonymous connection (no user logged in)")
            
            # Test 3: Test database operations
            print("\n🔍 Testing database operations...")
            if test_database_operations(supabase):
                print("\n🎉 All tests completed successfully!")
                return True
            else:
                print("\n❌ Database operations test failed")
                print("ℹ️  Note: This might be due to Row Level Security (RLS) policies. "
                      "Check your Supabase dashboard to ensure the anonymous role has the necessary permissions.")
                return False
                
        except Exception as e:
            # Check if this is a permission error (expected for anonymous access)
            if 'Invalid API key' in str(e):
                print("❌ Invalid API key. Please check your SUPABASE_ANON_KEY in the .env file.")
            elif 'permission denied' in str(e).lower():
                print("✅ Successfully connected to Supabase! (authentication check failed as expected for anonymous access)")
                print("ℹ️  Note: This is expected behavior for anonymous access.")
                
                # Even with anonymous access, we can still test database operations
                print("\n🔍 Testing database operations with anonymous access...")
                if test_database_operations(supabase):
                    print("\n🎉 All tests completed successfully!")
                    return True
                else:
                    print("\n❌ Database operations test failed")
                    print("ℹ️  Note: This might be due to Row Level Security (RLS) policies. "
                          "Check your Supabase dashboard to ensure the anonymous role has the necessary permissions.")
                    return False
            else:
                print(f"❌ Error testing auth endpoint: {str(e)}")
            return False
            
    except Exception as e:
        print(f"❌ Error connecting to Supabase: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing Supabase connection...")
    test_supabase_connection()
