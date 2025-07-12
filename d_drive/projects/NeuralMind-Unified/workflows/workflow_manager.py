"""
Workflow Manager - Handles n8n workflow automation and agent orchestration
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)


class WorkflowManager:
    """Manages n8n workflows and agent orchestration"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.n8n_url = config.get("n8n_url", "http://localhost:5678")
        self.auto_start = config.get("auto_start", [])

        # HTTP client
        self.http_client = None

        # Workflow state
        self.active_workflows = {}
        self.workflow_history = []

        self.is_initialized = False

    async def initialize(self):
        """Initialize the workflow manager"""
        try:
            logger.info("Initializing WorkflowManager...")

            # Create HTTP client
            self.http_client = httpx.AsyncClient(timeout=30.0)

            # Check n8n service
            await self._check_n8n_service()

            # Load available workflows
            await self._load_workflows()

            # Start auto-start workflows
            if self.auto_start:
                await self._start_auto_workflows()

            self.is_initialized = True
            logger.info("WorkflowManager initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing WorkflowManager: {e}")
            raise

    async def start(self):
        """Start the workflow manager"""
        if not self.is_initialized:
            await self.initialize()
        logger.info("WorkflowManager started")

    async def stop(self):
        """Stop the workflow manager"""
        # Stop all active workflows
        for workflow_id in list(self.active_workflows.keys()):
            await self.stop_workflow(workflow_id)

        if self.http_client:
            await self.http_client.aclose()

        logger.info("WorkflowManager stopped")

    async def health_check(self) -> bool:
        """Check if workflow manager is healthy"""
        try:
            if not self.http_client:
                return False

            # Check n8n health
            response = await self.http_client.get(f"{self.n8n_url}/healthz")
            return response.status_code == 200

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    async def _check_n8n_service(self):
        """Check if n8n service is available"""
        try:
            response = await self.http_client.get(f"{self.n8n_url}/healthz")
            if response.status_code != 200:
                raise Exception("n8n service not available")

            logger.info("n8n service is available")

        except Exception as e:
            logger.error(f"n8n service check failed: {e}")
            raise

    async def _load_workflows(self):
        """Load available workflows from n8n"""
        try:
            # Get workflows from n8n API
            response = await self.http_client.get(f"{self.n8n_url}/api/v1/workflows")

            if response.status_code == 200:
                workflows = response.json()
                logger.info(f"Loaded {len(workflows)} workflows from n8n")
            else:
                logger.warning("Could not load workflows from n8n")

        except Exception as e:
            logger.error(f"Workflow loading error: {e}")

    async def _start_auto_workflows(self):
        """Start workflows that should auto-start"""
        for workflow_name in self.auto_start:
            try:
                await self.start_workflow_by_name(workflow_name)
            except Exception as e:
                logger.error(f"Error auto-starting workflow {workflow_name}: {e}")

    async def execute_workflow(
        self, workflow_id: str, input_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Execute a workflow with optional input data"""
        try:
            # Prepare execution data
            execution_data = {"workflowData": input_data or {}}

            # Execute workflow
            response = await self.http_client.post(
                f"{self.n8n_url}/api/v1/workflows/{workflow_id}/execute",
                json=execution_data,
            )

            response.raise_for_status()
            result = response.json()

            # Track execution
            execution_record = {
                "workflow_id": workflow_id,
                "input_data": input_data,
                "result": result,
                "timestamp": asyncio.get_event_loop().time(),
                "success": True,
            }

            self.workflow_history.append(execution_record)

            logger.info(f"Executed workflow {workflow_id} successfully")

            return {
                "success": True,
                "execution_id": result.get("data", {}).get("executionId"),
                "result": result,
            }

        except Exception as e:
            logger.error(f"Workflow execution error: {e}")

            # Track failed execution
            execution_record = {
                "workflow_id": workflow_id,
                "input_data": input_data,
                "error": str(e),
                "timestamp": asyncio.get_event_loop().time(),
                "success": False,
            }

            self.workflow_history.append(execution_record)

            return {"success": False, "error": str(e)}

    async def start_workflow_by_name(self, workflow_name: str) -> bool:
        """Start a workflow by name"""
        try:
            # First, find the workflow by name
            workflows = await self.list_workflows()

            target_workflow = None
            for workflow in workflows:
                if workflow.get("name") == workflow_name:
                    target_workflow = workflow
                    break

            if not target_workflow:
                logger.error(f"Workflow not found: {workflow_name}")
                return False

            workflow_id = target_workflow.get("id")
            return await self.start_workflow(workflow_id)

        except Exception as e:
            logger.error(f"Error starting workflow by name {workflow_name}: {e}")
            return False

    async def start_workflow(self, workflow_id: str) -> bool:
        """Start a workflow"""
        try:
            if workflow_id in self.active_workflows:
                logger.warning(f"Workflow {workflow_id} is already active")
                return True

            # Activate the workflow
            response = await self.http_client.patch(
                f"{self.n8n_url}/api/v1/workflows/{workflow_id}", json={"active": True}
            )

            response.raise_for_status()

            self.active_workflows[workflow_id] = {
                "started_at": asyncio.get_event_loop().time(),
                "status": "active",
            }

            logger.info(f"Started workflow: {workflow_id}")
            return True

        except Exception as e:
            logger.error(f"Error starting workflow {workflow_id}: {e}")
            return False

    async def stop_workflow(self, workflow_id: str) -> bool:
        """Stop a workflow"""
        try:
            # Deactivate the workflow
            response = await self.http_client.patch(
                f"{self.n8n_url}/api/v1/workflows/{workflow_id}", json={"active": False}
            )

            response.raise_for_status()

            if workflow_id in self.active_workflows:
                del self.active_workflows[workflow_id]

            logger.info(f"Stopped workflow: {workflow_id}")
            return True

        except Exception as e:
            logger.error(f"Error stopping workflow {workflow_id}: {e}")
            return False

    async def list_workflows(self) -> List[Dict[str, Any]]:
        """List all available workflows"""
        try:
            response = await self.http_client.get(f"{self.n8n_url}/api/v1/workflows")
            response.raise_for_status()

            workflows = response.json()
            return workflows.get("data", [])

        except Exception as e:
            logger.error(f"Error listing workflows: {e}")
            return []

    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get status of a specific workflow"""
        try:
            response = await self.http_client.get(
                f"{self.n8n_url}/api/v1/workflows/{workflow_id}"
            )
            response.raise_for_status()

            workflow_data = response.json()

            # Add our tracking information
            status = {
                "id": workflow_id,
                "name": workflow_data.get("name", ""),
                "active": workflow_data.get("active", False),
                "is_tracked": workflow_id in self.active_workflows,
            }

            if workflow_id in self.active_workflows:
                status.update(self.active_workflows[workflow_id])

            return status

        except Exception as e:
            logger.error(f"Error getting workflow status for {workflow_id}: {e}")
            return {"error": str(e)}

    async def create_simple_workflow(
        self, name: str, nodes: List[Dict[str, Any]]
    ) -> str:
        """Create a simple workflow programmatically"""
        try:
            workflow_data = {
                "name": name,
                "nodes": nodes,
                "connections": {},
                "active": False,
                "settings": {},
                "staticData": {},
            }

            response = await self.http_client.post(
                f"{self.n8n_url}/api/v1/workflows", json=workflow_data
            )

            response.raise_for_status()
            result = response.json()

            workflow_id = result.get("data", {}).get("id")
            logger.info(f"Created workflow: {name} (ID: {workflow_id})")

            return workflow_id

        except Exception as e:
            logger.error(f"Error creating workflow {name}: {e}")
            raise

    async def trigger_webhook_workflow(
        self, webhook_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Trigger a workflow via webhook"""
        try:
            webhook_url = f"{self.n8n_url}/webhook/{webhook_id}"

            response = await self.http_client.post(webhook_url, json=data)
            response.raise_for_status()

            result = response.json() if response.content else {}

            logger.info(f"Triggered webhook workflow: {webhook_id}")

            return {"success": True, "response": result}

        except Exception as e:
            logger.error(f"Webhook trigger error for {webhook_id}: {e}")
            return {"success": False, "error": str(e)}

    def get_workflow_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get workflow execution history"""
        if limit:
            return self.workflow_history[-limit:]
        return self.workflow_history

    def get_active_workflows(self) -> Dict[str, Any]:
        """Get list of active workflows"""
        return self.active_workflows.copy()

    def clear_history(self):
        """Clear workflow execution history"""
        self.workflow_history.clear()
        logger.info("Workflow history cleared")

    async def import_workflow_from_file(self, file_path: str) -> str:
        """Import a workflow from JSON file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                workflow_data = json.load(f)

            # Remove ID if present (let n8n assign new one)
            if "id" in workflow_data:
                del workflow_data["id"]

            response = await self.http_client.post(
                f"{self.n8n_url}/api/v1/workflows", json=workflow_data
            )

            response.raise_for_status()
            result = response.json()

            workflow_id = result.get("data", {}).get("id")
            workflow_name = workflow_data.get("name", "Imported Workflow")

            logger.info(f"Imported workflow: {workflow_name} (ID: {workflow_id})")

            return workflow_id

        except Exception as e:
            logger.error(f"Error importing workflow from {file_path}: {e}")
            raise
