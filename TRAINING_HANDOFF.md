# ML Training Pipeline - Handoff Documentation

**Status**: IN PROGRESS - ML Training System Implementation
**Last Updated**: 2025-10-19
**Progress**: 10% Complete

## 🎯 Mission

Build a complete ML training pipeline to train agents on real Blender projects, materials, textures, and techniques scraped from open-source repositories.

## 📊 Current Progress

### ✅ Completed
1. VoxelWeaver framework (reference system)
2. Workflow integration
3. Training infrastructure directories created
4. Blender file scraper (with checkpointing)

### 🔄 In Progress
- Data collection system

### ⏳ Todo
- [ ] Blender file parser (.blend file analysis)
- [ ] Dataset builder (convert scraped data to training format)
- [ ] Fine-tuning data formatters (Claude & GPT formats)
- [ ] Training orchestrator
- [ ] Model evaluation system
- [ ] Model deployment system
- [ ] Training documentation

## 📁 Project Structure

```
src/voxel/training/
├── data_collection/
│   ├── blender_scraper.py      ✅ DONE - Scrapes GitHub for .blend files
│   ├── blend_parser.py          ⏳ TODO - Parses .blend files
│   └── image_scraper.py         ⏳ TODO - Scrapes textures/images
├── dataset_builder/
│   ├── blender_dataset.py       ⏳ TODO - Builds training datasets
│   ├── material_dataset.py      ⏳ TODO - Material-specific datasets
│   └── code_dataset.py          ⏳ TODO - Python code datasets
├── fine_tuning/
│   ├── claude_formatter.py      ⏳ TODO - Anthropic fine-tuning format
│   ├── openai_formatter.py      ⏳ TODO - OpenAI fine-tuning format
│   └── training_orchestrator.py ⏳ TODO - Manages training jobs
└── evaluation/
    ├── quality_metrics.py       ⏳ TODO - Quality evaluation
    └── benchmark.py             ⏳ TODO - Benchmark system
```

## 🔧 Checkpoint System

### Location
All checkpoints saved to: `/Users/justin/Desktop/gthh/gtvibeathon/training_data/checkpoints/`

### Files
- `scraping_checkpoint.json` - Scraping progress
- `parsing_checkpoint.json` - Parsing progress
- `dataset_checkpoint.json` - Dataset building progress
- `training_checkpoint.json` - Training job status

### Checkpoint Format
```json
{
  "task": "scraping",
  "status": "in_progress",
  "started_at": "2025-10-19T18:45:00Z",
  "last_updated": "2025-10-19T18:50:00Z",
  "progress": {
    "total_queries": 9,
    "completed_queries": 3,
    "current_query": "blender materials .blend",
    "files_found": 145,
    "files_downloaded": 0,
    "errors": 2
  },
  "state": {
    "scraped_hashes": [...],
    "current_repo_index": 5,
    "rate_limit_reset_at": "2025-10-19T19:00:00Z"
  },
  "next_steps": [
    "Resume from query index 3",
    "Check rate limit status",
    "Continue scraping"
  ]
}
```

## 🚀 How to Continue (For Cursor/Next Session)

### Step 1: Check Current Status
```bash
cd /Users/justin/Desktop/gthh/gtvibeathon
cat training_data/checkpoints/scraping_checkpoint.json
```

### Step 2: Resume Data Collection
```python
from src.voxel.training.data_collection.blender_scraper import BlenderFileScraper
from pathlib import Path
import asyncio

# Load from checkpoint
scraper = BlenderFileScraper.from_checkpoint(
    Path("training_data/checkpoints/scraping_checkpoint.json")
)

# Resume scraping
stats = asyncio.run(scraper.resume_scraping())
print(f"Scraping resumed: {stats}")
```

### Step 3: Next Task - Blend File Parser
```bash
# Create: src/voxel/training/data_collection/blend_parser.py
# Requirements:
# - Parse .blend files using blender_file library
# - Extract: objects, materials, modifiers, node trees
# - Save structured data to JSON
# - Checkpoint every 10 files
```

## 📋 Implementation Checklist

### Phase 1: Data Collection (Current)
- [x] GitHub scraper
- [x] Checkpoint system
- [ ] Blend file parser
- [ ] Texture/image scraper
- [ ] Video scraper (optional)
- [ ] Quality filtering

### Phase 2: Dataset Building
- [ ] Convert .blend data to training examples
- [ ] Create prompt-completion pairs
- [ ] Material knowledge extraction
- [ ] Code pattern extraction
- [ ] Validation and cleaning

### Phase 3: Fine-Tuning Setup
- [ ] Format data for Claude fine-tuning
- [ ] Format data for GPT fine-tuning
- [ ] Split train/val/test sets
- [ ] Upload to training platforms
- [ ] Configure training parameters

### Phase 4: Training Execution
- [ ] Submit Claude fine-tuning job
- [ ] Submit GPT fine-tuning job
- [ ] Monitor training metrics
- [ ] Evaluate checkpoints
- [ ] Select best models

### Phase 5: Deployment
- [ ] Deploy fine-tuned models
- [ ] A/B testing framework
- [ ] Performance monitoring
- [ ] Continuous improvement

## 🔑 Required API Keys & Resources

### GitHub
- **Token**: Set `GITHUB_TOKEN` env var
- **Rate Limit**: 5000 requests/hour with token
- **Get Token**: https://github.com/settings/tokens

### Anthropic (Claude Fine-tuning)
- **API Key**: In `.env` as `ANTHROPIC_API_KEY`
- **Docs**: https://docs.anthropic.com/claude/docs/fine-tuning
- **Cost**: ~$0.50 per 1K training tokens

### OpenAI (GPT Fine-tuning)
- **API Key**: In `.env` as `OPENAI_API_KEY`
- **Docs**: https://platform.openai.com/docs/guides/fine-tuning
- **Cost**: ~$8.00 per 1M training tokens (GPT-4)

## 📊 Expected Training Data Scale

### Target Dataset Size
- **Blender Files**: 500-1000 files
- **Training Examples**: 10,000-50,000
- **Total Data**: ~5-10 GB
- **Training Time**: 2-12 hours per model
- **Cost Estimate**: $200-500 total

### Quality Thresholds
- Minimum 10 GitHub stars
- Valid .blend file format
- Open source license
- No errors on parse

## ⚠️ Known Issues & Solutions

### Issue 1: GitHub Rate Limiting
**Problem**: API rate limits (60/hour without token, 5000/hour with token)
**Solution**:
- Checkpoint after each query
- Auto-resume after rate limit reset
- Use multiple tokens (if available)

### Issue 2: Large File Sizes
**Problem**: .blend files can be 100MB+
**Solution**:
- Download only metadata first
- Filter by size before download
- Stream downloads
- Store in efficient format

### Issue 3: Parsing Complexity
**Problem**: .blend files are complex binary format
**Solution**:
- Use `blender_file` Python library
- Fall back to Blender Python API if needed
- Extract only essential data

## 🔄 Resume Points

If interrupted, resume from these checkpoints:

1. **After Scraping**: `training_data/scraped_metadata.json` exists
2. **After Parsing**: `training_data/parsed_data/*.json` exist
3. **After Dataset Building**: `training_data/datasets/` populated
4. **After Training Submission**: `training_data/training_jobs.json` has job IDs

## 📞 Handoff Protocol

When handing off to next session:

1. **Update** this document with current progress
2. **Commit** all checkpoint files
3. **Document** any errors or blockers
4. **List** exact next steps
5. **Provide** any new API keys or credentials needed

## 🎯 Success Criteria

Training pipeline is complete when:

- [ ] 500+ Blender files scraped and parsed
- [ ] 10,000+ training examples created
- [ ] Claude model fine-tuned and deployed
- [ ] GPT model fine-tuned and deployed
- [ ] Quality metrics show >20% improvement
- [ ] Production deployment successful

## 📝 Notes

- Backend currently running on port 5002
- VoxelWeaver reference system is operational
- Use existing `.env` for API keys
- Training data saved to `./training_data/`

---

**Next Session Should Start With**: Creating `blend_parser.py` to parse downloaded .blend files
