# Voxel Database System

## Overview

The Voxel database system provides comprehensive tracking of all projects, generations, agent executions, scripts, renders, and analytics. Built on SQLite with SQLAlchemy ORM, it offers a robust foundation for project management and system analytics.

## Database Schema

### Core Tables

#### Projects
- **projects**: Top-level project tracking
  - `id` (PRIMARY KEY)
  - `name` (VARCHAR)
  - `description` (TEXT)
  - `created_at` (DATETIME)
  - `updated_at` (DATETIME)
  - `status` (ENUM: draft, in_progress, completed, archived)
  - `settings_json` (JSON)

#### Generations
- **generations**: Individual scene generation attempts
  - `id` (PRIMARY KEY)
  - `project_id` (FOREIGN KEY → projects.id)
  - `session_id` (VARCHAR) - links to output folder
  - `prompt` (TEXT) - original user prompt
  - `created_at` (DATETIME)
  - `completed_at` (DATETIME)
  - `status` (ENUM: pending, running, completed, failed)
  - `iteration_count` (INTEGER)
  - `quality_score` (FLOAT)
  - `output_path` (VARCHAR)

#### Agent Executions
- **agent_executions**: Track each agent's work
  - `id` (PRIMARY KEY)
  - `generation_id` (FOREIGN KEY → generations.id)
  - `agent_type` (ENUM: concept, builder, texture, render, animation, reviewer)
  - `iteration_number` (INTEGER)
  - `prompt` (TEXT)
  - `response_text` (TEXT)
  - `execution_time_ms` (INTEGER)
  - `token_count` (INTEGER)
  - `created_at` (DATETIME)
  - `status` (ENUM: success, failed)
  - `error_message` (TEXT)

#### Scripts
- **scripts**: Generated Blender scripts
  - `id` (PRIMARY KEY)
  - `generation_id` (FOREIGN KEY → generations.id)
  - `agent_type` (ENUM)
  - `iteration_number` (INTEGER)
  - `script_content` (TEXT) - full script
  - `file_path` (VARCHAR)
  - `created_at` (DATETIME)

#### Renders
- **renders**: Rendered outputs
  - `id` (PRIMARY KEY)
  - `generation_id` (FOREIGN KEY → generations.id)
  - `iteration_number` (INTEGER)
  - `file_path` (VARCHAR)
  - `render_time_seconds` (FLOAT)
  - `samples` (INTEGER)
  - `resolution_x` (INTEGER)
  - `resolution_y` (INTEGER)
  - `engine` (ENUM: CYCLES, EEVEE)
  - `created_at` (DATETIME)

#### Reviews
- **reviews**: Reviewer agent feedback
  - `id` (PRIMARY KEY)
  - `generation_id` (FOREIGN KEY → generations.id)
  - `iteration_number` (INTEGER)
  - `rating` (INTEGER) - 1-10 scale
  - `feedback_text` (TEXT)
  - `suggestions` (TEXT)
  - `created_at` (DATETIME)

#### Tags
- **tags**: Categorization tags
  - `id` (PRIMARY KEY)
  - `name` (VARCHAR, UNIQUE)
  - `category` (VARCHAR)
  - `created_at` (DATETIME)

#### Generation Tags
- **generation_tags**: Many-to-many relationship
  - `generation_id` (FOREIGN KEY → generations.id)
  - `tag_id` (FOREIGN KEY → tags.id)
  - `created_at` (DATETIME)

#### Analytics
- **analytics**: Usage statistics
  - `id` (PRIMARY KEY)
  - `date` (DATETIME)
  - `total_generations` (INTEGER)
  - `successful_generations` (INTEGER)
  - `avg_quality_score` (FLOAT)
  - `avg_render_time` (FLOAT)
  - `total_tokens_used` (INTEGER)
  - `total_cost_estimate` (FLOAT)
  - `created_at` (DATETIME)

## Usage Examples

### Basic Database Operations

```python
from voxel import Voxel

# Initialize Voxel (creates database automatically)
voxel = Voxel()

# Create a new project
project = voxel.create_project(
    name="My Scene Project",
    description="A test project for learning Voxel",
    settings={"render_samples": 256, "engine": "CYCLES"}
)

# Get all projects
projects = voxel.get_projects()

# Get project history
history = voxel.get_project_history(project["id"])

# Get system analytics
analytics = voxel.get_system_analytics(days=30)

# Close the agency
voxel.close()
```

### Advanced Database Queries

```python
from agency3d.database import DatabaseManager, DatabaseQueries

# Initialize database manager directly
db_manager = DatabaseManager()
db_queries = DatabaseQueries(db_manager)

# Get recent generations
recent = db_queries.get_recent_generations(limit=10)

# Get agent performance
concept_perf = db_queries.get_agent_performance("concept", days=30)

# Search generations
results = db_queries.search_generations("cyberpunk", limit=20)

# Get quality trends
trends = db_queries.get_quality_trends(days=7)

# Close database
db_manager.close()
```

### CLI Database Commands

```bash
# List all projects
voxel list-projects

# Show project history
voxel project-history 1

# Show system statistics
voxel stats --days 30

# Search generations
voxel search "cyberpunk" --limit 10

# Create a new project
voxel create-project "My Project" --description "A test project"
```

## Database Management

### Initialization

The database is automatically created when you first initialize `Voxel`:

```python
from voxel import Voxel

# This creates the database and all tables
voxel = Voxel()
```

### Configuration

Database settings can be configured in your `.env` file:

```env
# Database configuration
DATABASE_URL=sqlite:///database/voxel.db
DATABASE_ECHO=false
```

### Migrations

The database system includes migration support for schema updates:

```python
from agency3d.database import MigrationManager

# Initialize migration manager
migration_manager = MigrationManager(db_manager)

# Create a new migration
migration_file = migration_manager.create_migration(
    "add_new_field",
    "Add new field to projects table"
)

# Run all pending migrations
results = migration_manager.run_all_pending_migrations()
```

### Backup and Restore

```python
# Create a backup
backup_path = migration_manager.backup_database()

# Restore from backup
success = migration_manager.restore_database(backup_path)
```

## Analytics and Reporting

### System Analytics

```python
# Get comprehensive system analytics
analytics = voxel.get_system_analytics(days=30)

print(f"Total generations: {analytics['total_generations']}")
print(f"Success rate: {analytics['success_rate']:.1f}%")
print(f"Average quality: {analytics['avg_quality']:.2f}")
print(f"Total render time: {analytics['total_render_time']:.1f}s")
print(f"Total tokens: {analytics['total_tokens']}")
```

### Agent Performance

```python
# Get performance metrics for each agent
agents = ["concept", "builder", "texture", "render", "animation", "reviewer"]

for agent_type in agents:
    perf = voxel.get_agent_performance(agent_type, days=30)
    print(f"{agent_type}: {perf['total_executions']} executions, "
          f"{perf['success_rate']:.1f}% success rate")
```

### Quality Trends

```python
# Get quality score trends over time
trends = voxel.get_quality_trends(days=7)

for trend in trends:
    print(f"{trend['date']}: {trend['avg_quality']:.2f} "
          f"({trend['count']} generations)")
```

## Database Schema Diagram

```
projects (1) ──→ (many) generations
                    │
                    ├──→ (many) agent_executions
                    ├──→ (many) scripts
                    ├──→ (many) renders
                    ├──→ (many) reviews
                    └──→ (many) generation_tags ──→ (many) tags

analytics (standalone table for daily statistics)
```

## Performance Considerations

### Indexes

The database includes several indexes for optimal query performance:

- `idx_agent_executions_generation` on `agent_executions.generation_id`
- `idx_agent_executions_agent_type` on `agent_executions.agent_type`
- `idx_agent_executions_created` on `agent_executions.created_at`
- `idx_scripts_generation` on `scripts.generation_id`
- `idx_scripts_agent_type` on `scripts.agent_type`
- `idx_renders_generation` on `renders.generation_id`
- `idx_renders_created` on `renders.created_at`
- `idx_reviews_generation` on `reviews.generation_id`
- `idx_reviews_rating` on `reviews.rating`
- `idx_analytics_date` on `analytics.date`

### Query Optimization

- Use specific date ranges for analytics queries
- Limit result sets with appropriate `LIMIT` clauses
- Use indexes for filtering on foreign keys and dates
- Consider archiving old data for large-scale deployments

## Troubleshooting

### Common Issues

1. **Database locked**: Ensure only one process is accessing the database at a time
2. **Schema inconsistencies**: Run `migration_manager.check_schema_consistency()`
3. **Performance issues**: Check if indexes are being used effectively
4. **Disk space**: Monitor database file size and consider archiving old data

### Debugging

```python
# Check database connection
if db_manager.check_connection():
    print("Database connection successful")
else:
    print("Database connection failed")

# Check schema consistency
consistency = migration_manager.check_schema_consistency()
if not consistency['consistent']:
    print(f"Schema issues: {consistency}")

# Get database schema information
schema = migration_manager.get_database_schema()
print(f"Database has {schema['total_tables']} tables")
```

## Future Enhancements

- **PostgreSQL support**: For production deployments
- **Data archiving**: Automatic archiving of old data
- **Real-time analytics**: Live dashboard updates
- **Export functionality**: Export data to various formats
- **Advanced reporting**: Custom report generation
- **Data visualization**: Built-in charts and graphs
