"""
Logging service for synchronization runs.
"""

import os
from datetime import datetime, timezone

class SyncLogger:
    def __init__(self, supabase_client):
        self.client = supabase_client
        self.run_id = None

    def start_run(self, cards_total: int):
        """
        Start a new synchronization run log entry.

        Args:
            cards_total: Total number of cards to process.
        Returns:
            int: ID of the created sync run.            
        """
        payload = {
            "status": "running",
            "cards_total": cards_total,
            "cards_processed": 0,
            "cards_skipped": 0,
            "cards_failed": 0,
            "run_source": "github-actions" if os.environ.get("GITHUB_ACTIONS") else "local",
            "git_sha": os.environ.get("GITHUB_SHA"),
            "started_at": datetime.now(timezone.utc).isoformat(),
        }
        res = self.client.table("sync_runs").insert(payload).execute()
        self.run_id = res.data[0]["id"]
        return self.run_id

    def log_failure(self, card_id: str, step: str, err: Exception):
        """
        Log a failure for a specific card during synchronization.

        Args:
            card_id: ID of the Trello card.
            step: Step during which the error occurred.
            err: Exception instance.

        Returns:
            None        
        """

    
        if not self.run_id:
            return
        msg = f"{type(err).__name__}: {str(err)}"
        payload = {
            "run_id": self.run_id,
            "card_id": card_id,
            "step": step,
            "error": msg[:1000],
        }
        self.client.table("sync_failures").insert(payload).execute()

    def finish_run(self, status: str, processed: int, skipped: int, failed: int, run_error: str | None = None):
        """
        Finish the synchronization run log entry.

        Args:
            status: Final status of the run ("completed", "failed", etc.).  
            processed: Number of cards processed.
            skipped: Number of cards skipped.
            failed: Number of cards that failed.
            run_error: Optional error message if the run failed.
        Returns:
            None    
        """

        if not self.run_id:
            return
        payload = {
            "status": status,
            "cards_processed": processed,
            "cards_skipped": skipped,
            "cards_failed": failed,
            "error": run_error[:1000] if run_error else None,
            "finished_at": datetime.now(timezone.utc).isoformat(),
        }
        self.client.table("sync_runs").update(payload).eq("id", self.run_id).execute()
