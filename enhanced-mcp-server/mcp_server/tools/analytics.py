# Analytics tools for the Enhanced MCP Server

from fastmcp import FastMCP, Context
import structlog
from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from ..core.server import get_server
from ..models import AppliedJob

logger = structlog.get_logger(__name__)

async def get_application_analytics(ctx: Context) -> Dict[str, Any]:
    """
    Calculates and returns application analytics.
    """
    server = get_server()
    db_manager = server.database_manager
    db_gen = db_manager.get_db()
    db: Session = next(db_gen)

    try:
        total_applications = db.query(AppliedJob).count()
        
        status_counts = db.query(AppliedJob.application_status, func.count(AppliedJob.id)).group_by(AppliedJob.application_status).all()
        status_counts_dict = {status: count for status, count in status_counts}

        success_statuses = ['interview', 'offer']
        successful_applications = sum(status_counts_dict.get(status, 0) for status in success_statuses)
        success_rate = (successful_applications / total_applications * 100) if total_applications > 0 else 0

        return {
            "status": "success",
            "analytics": {
                "total_applications": total_applications,
                "status_counts": status_counts_dict,
                "success_rate": round(success_rate, 1),
            }
        }
    except Exception as e:
        logger.error("An error occurred during analytics calculation", error=str(e))
        return {"status": "error", "message": f"An error occurred: {e}"}
    finally:
        db.close()

def register_tools(mcp: FastMCP):
    mcp.tool()(get_application_analytics)