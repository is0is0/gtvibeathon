"""
Database Usage Examples for Voxel.

This module demonstrates how to use the Voxel database system for tracking
projects, generations, and analytics.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from voxel import Voxel
from voxel.database import DatabaseManager, DatabaseQueries


def basic_database_usage():
    """Demonstrate basic database operations."""
    print("=== Basic Database Usage ===")
    
    # Initialize Voxel (this will create the database)
    voxel = Voxel()
    
    # Create a new project
    project = voxel.create_project(
        name="My First Project",
        description="A test project for learning Voxel",
        settings={"render_samples": 256, "engine": "CYCLES"}
    )
    print(f"Created project: {project['name']} (ID: {project['id']})")
    
    # Get all projects
    projects = voxel.get_projects()
    print(f"Total projects: {len(projects)}")
    
    # Get project statistics
    stats = voxel.get_project_statistics(project['id'])
    print(f"Project statistics: {stats}")
    
    # Get system analytics
    analytics = voxel.get_system_analytics(days=30)
    print(f"System analytics: {analytics}")
    
    # Close the voxel
    voxel.close()


def advanced_database_queries():
    """Demonstrate advanced database queries."""
    print("\n=== Advanced Database Queries ===")
    
    # Initialize database manager directly
    db_manager = DatabaseManager()
    db_queries = DatabaseQueries(db_manager)
    
    # Get recent generations
    recent = db_queries.get_recent_generations(limit=5)
    print(f"Recent generations: {len(recent)}")
    
    # Get agent performance
    concept_performance = db_queries.get_agent_performance("concept", days=30)
    print(f"Concept agent performance: {concept_performance}")
    
    # Get quality trends
    trends = db_queries.get_quality_trends(days=7)
    print(f"Quality trends: {len(trends)} data points")
    
    # Search generations
    search_results = db_queries.search_generations("house", limit=10)
    print(f"Search results for 'house': {len(search_results)}")
    
    # Get failed generations
    failed = db_queries.get_failed_generations(limit=5)
    print(f"Failed generations: {len(failed)}")
    
    # Close database
    db_manager.close()


def database_analytics():
    """Demonstrate database analytics features."""
    print("\n=== Database Analytics ===")
    
    agency = Agency3D()
    
    # Get system-wide analytics
    analytics = voxel.get_system_analytics(days=30)
    print("System Analytics (30 days):")
    print(f"  Total generations: {analytics.get('total_generations', 0)}")
    print(f"  Success rate: {analytics.get('success_rate', 0):.1f}%")
    print(f"  Average quality: {analytics.get('avg_quality', 0):.2f}")
    print(f"  Total render time: {analytics.get('total_render_time', 0):.1f}s")
    print(f"  Total tokens: {analytics.get('total_tokens', 0)}")
    
    # Get quality trends
    trends = voxel.get_quality_trends(days=7)
    if trends:
        print(f"\nQuality Trends (7 days):")
        for trend in trends[-3:]:  # Show last 3 days
            print(f"  {trend['date']}: {trend['avg_quality']:.2f} ({trend['count']} generations)")
    
    # Get agent performance
    agents = ["concept", "builder", "texture", "render", "animation", "reviewer"]
    print(f"\nAgent Performance (30 days):")
    for agent_type in agents:
        perf = voxel.get_agent_performance(agent_type, days=30)
        if perf['total_executions'] > 0:
            print(f"  {agent_type}: {perf['total_executions']} executions, "
                  f"{perf['success_rate']:.1f}% success, "
                  f"{perf['avg_time_ms']:.0f}ms avg time")
    
    voxel.close()


def project_management():
    """Demonstrate project management features."""
    print("\n=== Project Management ===")
    
    agency = Agency3D()
    
    # Create multiple projects
    projects = [
        ("Cyberpunk City", "A futuristic cityscape with neon lights"),
        ("Medieval Castle", "A detailed castle with towers and walls"),
        ("Modern House", "A contemporary residential building")
    ]
    
    created_projects = []
    for name, description in projects:
        project = voxel.create_project(name, description)
        created_projects.append(project)
        print(f"Created: {project['name']}")
    
    # Get all projects
    all_projects = voxel.get_projects()
    print(f"\nTotal projects: {len(all_projects)}")
    
    # Get project history for first project
    if created_projects:
        first_project = created_projects[0]
        history = voxel.get_project_history(first_project['id'])
        print(f"\nProject history for '{first_project['name']}': {len(history)} generations")
    
    # Search projects
    search_results = voxel.search_generations("cyberpunk", limit=5)
    print(f"\nSearch results for 'cyberpunk': {len(search_results)}")
    
    voxel.close()


def database_maintenance():
    """Demonstrate database maintenance operations."""
    print("\n=== Database Maintenance ===")
    
    from agency3d.database import MigrationManager
    
    # Initialize database manager
    db_manager = DatabaseManager()
    migration_manager = MigrationManager(db_manager)
    
    # Check database connection
    if db_manager.check_connection():
        print("✓ Database connection successful")
    else:
        print("✗ Database connection failed")
        return
    
    # Get database schema
    schema = migration_manager.get_database_schema()
    print(f"Database has {schema.get('total_tables', 0)} tables")
    
    # Check schema consistency
    consistency = migration_manager.check_schema_consistency()
    if consistency.get('consistent', False):
        print("✓ Database schema is consistent")
    else:
        print("✗ Database schema issues found:")
        if consistency.get('missing_tables'):
            print(f"  Missing tables: {consistency['missing_tables']}")
        if consistency.get('extra_tables'):
            print(f"  Extra tables: {consistency['extra_tables']}")
    
    # Create a backup
    backup_path = migration_manager.backup_database()
    if backup_path:
        print(f"✓ Database backed up to: {backup_path}")
    else:
        print("✗ Database backup failed")
    
    db_manager.close()


if __name__ == "__main__":
    """Run all database examples."""
    print("Voxel Database Usage Examples")
    print("=" * 40)
    
    try:
        basic_database_usage()
        advanced_database_queries()
        database_analytics()
        project_management()
        database_maintenance()
        
        print("\n✓ All examples completed successfully!")
        
    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        import traceback
        traceback.print_exc()
