import os
import pytest
from linkedin_browser_mcp import (
    login_linkedin_secure,
    browse_linkedin_feed,
    search_linkedin_profiles,
    search_linkedin_jobs,
    apply_to_linkedin_job,
    save_linkedin_job,
    get_job_recommendations,
    list_applied_jobs,
    list_saved_jobs
)

class MockContext:
    def info(self, message):
        print(f"INFO: {message}")
    def error(self, message):
        print(f"ERROR: {message}")
    async def report_progress(self, current, total):
        print(f"Progress: {current}/{total}")

@pytest.mark.asyncio
async def test_login_linkedin_secure_success():
    ctx = MockContext()
    # Ensure environment credentials are in place
    result = await login_linkedin_secure(ctx)
    assert result["status"] == "success"
    assert "successful" in result["message"].lower()

@pytest.mark.asyncio
async def test_browse_linkedin_feed_success():
    ctx = MockContext()
    result = await browse_linkedin_feed(ctx, count=3)
    assert result["status"] == "success"
    assert isinstance(result.get("posts"), list)
    assert len(result.get("posts", [])) > 0

@pytest.mark.asyncio
async def test_search_linkedin_profiles_success():
    ctx = MockContext()
    result = await search_linkedin_profiles("Python", ctx, count=3)
    assert result["status"] == "success"
    assert isinstance(result.get("profiles"), list)
    assert len(result.get("profiles", [])) > 0

@pytest.mark.asyncio
async def test_search_linkedin_jobs_success():
    ctx = MockContext()
    result = await search_linkedin_jobs("Software Engineer", ctx, location="Remote", count=3)
    assert result["status"] == "success"
    assert isinstance(result.get("jobs"), list)
    assert len(result.get("jobs", [])) > 0

@pytest.mark.asyncio
async def test_get_job_recommendations_success():
    ctx = MockContext()
    result = await get_job_recommendations(ctx)
    assert result["status"] == "success"
    assert isinstance(result.get("recommended_jobs"), list)
    assert len(result.get("recommended_jobs", [])) > 0

@pytest.mark.asyncio
async def test_apply_and_list_applied_jobs():
    ctx = MockContext()
    # Search for at least one job to apply
    search_res = await search_linkedin_jobs("Software Engineer", ctx, location="Remote", count=1)
    if search_res.get("status") != "success" or not search_res.get("jobs"):
        pytest.skip("No jobs available to apply to")
    job_url = search_res["jobs"][0]["jobUrl"]
    apply_res = await apply_to_linkedin_job(job_url, ctx)
    assert apply_res["status"] in ("success", "partial")
    list_res = await list_applied_jobs(ctx)
    assert list_res["status"] == "success"
    assert any(job.get("job_url") == job_url for job in list_res.get("applied_jobs", []))

@pytest.mark.asyncio
async def test_save_and_list_saved_jobs():
    ctx = MockContext()
    # Search for at least one job to save
    search_res = await search_linkedin_jobs("Software Engineer", ctx, location="Remote", count=1)
    if search_res.get("status") != "success" or not search_res.get("jobs"):
        pytest.skip("No jobs available to save")
    job_url = search_res["jobs"][0]["jobUrl"]
    save_res = await save_linkedin_job(job_url, ctx)
    assert save_res["status"] == "success"
    list_res = await list_saved_jobs(ctx)
    assert list_res["status"] == "success"
    assert any(job.get("job_url") == job_url for job in list_res.get("saved_jobs", []))