"""
Agent Framework
---------------
Lightweight message-passing system for asynchronous AI agent coordination.

Implements an actor-based architecture where each subsystem is an autonomous
agent that communicates via asyncio queues.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import uuid
from utils.logger import get_logger

logger = get_logger(__name__)


class MessageType(str, Enum):
    """Types of messages in the system."""
    REQUEST = "request"           # Request to perform task
    RESPONSE = "response"          # Response with results
    ERROR = "error"                # Error occurred
    STATUS = "status"              # Status update
    CANCEL = "cancel"              # Cancel operation
    HEARTBEAT = "heartbeat"        # Keep-alive signal


class MessagePriority(int, Enum):
    """Message priority levels."""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


@dataclass
class Message:
    """Message passed between agents."""
    message_id: str
    message_type: MessageType
    sender: str
    recipient: str
    data: Dict[str, Any] = field(default_factory=dict)
    priority: MessagePriority = MessagePriority.NORMAL
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    reply_to: Optional[str] = None  # For request-response pairing
    timeout: Optional[float] = None  # Timeout in seconds

    def __lt__(self, other):
        """Compare by priority for priority queue."""
        return self.priority.value > other.priority.value  # Higher priority first


@dataclass
class AgentResult:
    """Result returned by an agent."""
    success: bool
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    duration: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgentInterface(ABC):
    """
    Base interface for all AI agents in the system.

    Each agent runs in its own asyncio task and communicates via message queues.
    Agents can process messages concurrently and maintain their own state.
    """

    def __init__(self, agent_name: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize agent.

        Args:
            agent_name: Unique name for this agent
            config: Optional configuration dictionary
        """
        self.agent_name = agent_name
        self.config = config or {}

        # Message queues
        self.inbox = asyncio.PriorityQueue()  # Incoming messages
        self.outbox = asyncio.Queue()         # Outgoing messages

        # Agent state
        self.running = False
        self.task = None
        self.pending_requests: Dict[str, asyncio.Future] = {}

        # Statistics
        self.stats = {
            'messages_received': 0,
            'messages_sent': 0,
            'tasks_completed': 0,
            'tasks_failed': 0,
            'total_processing_time': 0.0
        }

        logger.info(f"Agent '{agent_name}' initialized")

    async def start(self):
        """Start the agent's message processing loop."""
        if self.running:
            logger.warning(f"Agent '{self.agent_name}' already running")
            return

        self.running = True
        self.task = asyncio.create_task(self._run())
        logger.info(f"Agent '{self.agent_name}' started")

    async def stop(self):
        """Stop the agent gracefully."""
        self.running = False

        if self.task:
            # Cancel any pending tasks
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass

        logger.info(f"Agent '{self.agent_name}' stopped")

    async def send_message(self, message: Message):
        """
        Send message to outbox.

        Args:
            message: Message to send
        """
        await self.outbox.put(message)
        self.stats['messages_sent'] += 1

    async def request(
        self,
        recipient: str,
        data: Dict[str, Any],
        timeout: Optional[float] = 30.0
    ) -> AgentResult:
        """
        Send request and wait for response.

        Args:
            recipient: Target agent name
            data: Request data
            timeout: Timeout in seconds

        Returns:
            Agent result from recipient
        """
        message_id = str(uuid.uuid4())

        # Create future for response
        future = asyncio.Future()
        self.pending_requests[message_id] = future

        # Send request
        request = Message(
            message_id=message_id,
            message_type=MessageType.REQUEST,
            sender=self.agent_name,
            recipient=recipient,
            data=data,
            timeout=timeout
        )

        await self.send_message(request)

        try:
            # Wait for response with timeout
            result = await asyncio.wait_for(future, timeout=timeout)
            return result
        except asyncio.TimeoutError:
            logger.error(f"Request {message_id} to {recipient} timed out")
            return AgentResult(
                success=False,
                error=f"Request timed out after {timeout}s"
            )
        finally:
            # Clean up
            self.pending_requests.pop(message_id, None)

    async def _run(self):
        """Main message processing loop."""
        logger.info(f"Agent '{self.agent_name}' message loop started")

        while self.running:
            try:
                # Wait for message with timeout for heartbeat
                priority, message = await asyncio.wait_for(
                    self.inbox.get(),
                    timeout=1.0
                )

                self.stats['messages_received'] += 1

                # Process message based on type
                if message.message_type == MessageType.REQUEST:
                    await self._handle_request(message)
                elif message.message_type == MessageType.RESPONSE:
                    await self._handle_response(message)
                elif message.message_type == MessageType.ERROR:
                    await self._handle_error(message)
                elif message.message_type == MessageType.CANCEL:
                    await self._handle_cancel(message)
                else:
                    logger.warning(f"Unknown message type: {message.message_type}")

            except asyncio.TimeoutError:
                # No message received, continue (allows checking running flag)
                continue
            except asyncio.CancelledError:
                logger.info(f"Agent '{self.agent_name}' task cancelled")
                break
            except Exception as e:
                logger.error(f"Error in agent '{self.agent_name}': {e}", exc_info=True)

    async def _handle_request(self, message: Message):
        """
        Handle incoming request message.

        Args:
            message: Request message
        """
        start_time = asyncio.get_event_loop().time()

        try:
            # Process request using abstract method
            result = await self.process_task(message.data)

            # Update stats
            duration = asyncio.get_event_loop().time() - start_time
            self.stats['tasks_completed'] += 1
            self.stats['total_processing_time'] += duration

            result.duration = duration

            # Send response
            response = Message(
                message_id=str(uuid.uuid4()),
                message_type=MessageType.RESPONSE,
                sender=self.agent_name,
                recipient=message.sender,
                data={'result': result.__dict__},
                reply_to=message.message_id
            )

            await self.send_message(response)

        except Exception as e:
            self.stats['tasks_failed'] += 1
            logger.error(f"Error processing request in '{self.agent_name}': {e}", exc_info=True)

            # Send error response
            error_response = Message(
                message_id=str(uuid.uuid4()),
                message_type=MessageType.ERROR,
                sender=self.agent_name,
                recipient=message.sender,
                data={'error': str(e)},
                reply_to=message.message_id
            )

            await self.send_message(error_response)

    async def _handle_response(self, message: Message):
        """
        Handle response to our request.

        Args:
            message: Response message
        """
        if message.reply_to and message.reply_to in self.pending_requests:
            future = self.pending_requests[message.reply_to]

            # Extract result from message
            result_data = message.data.get('result', {})
            result = AgentResult(**result_data)

            # Set future result
            if not future.done():
                future.set_result(result)

    async def _handle_error(self, message: Message):
        """
        Handle error message.

        Args:
            message: Error message
        """
        logger.error(f"Error from '{message.sender}': {message.data.get('error')}")

        if message.reply_to and message.reply_to in self.pending_requests:
            future = self.pending_requests[message.reply_to]

            result = AgentResult(
                success=False,
                error=message.data.get('error', 'Unknown error')
            )

            if not future.done():
                future.set_result(result)

    async def _handle_cancel(self, message: Message):
        """
        Handle cancellation request.

        Args:
            message: Cancel message
        """
        logger.info(f"Cancel request received in '{self.agent_name}'")
        # Implement cancellation logic if needed
        pass

    @abstractmethod
    async def process_task(self, data: Dict[str, Any]) -> AgentResult:
        """
        Process a task request.

        This method should be implemented by each specific agent.

        Args:
            data: Task data from request message

        Returns:
            Result of task processing
        """
        pass

    def get_stats(self) -> Dict[str, Any]:
        """
        Get agent statistics.

        Returns:
            Statistics dictionary
        """
        avg_time = (
            self.stats['total_processing_time'] / self.stats['tasks_completed']
            if self.stats['tasks_completed'] > 0 else 0.0
        )

        return {
            **self.stats,
            'average_processing_time': avg_time,
            'success_rate': (
                self.stats['tasks_completed'] /
                (self.stats['tasks_completed'] + self.stats['tasks_failed'])
                if (self.stats['tasks_completed'] + self.stats['tasks_failed']) > 0
                else 0.0
            )
        }


class MessageBus:
    """
    Central message bus for routing messages between agents.

    Acts as a mediator, routing messages from agent outboxes to recipient inboxes.
    """

    def __init__(self):
        """Initialize message bus."""
        self.agents: Dict[str, AgentInterface] = {}
        self.running = False
        self.task = None

        # Statistics
        self.total_messages = 0
        self.messages_by_type: Dict[MessageType, int] = {
            msg_type: 0 for msg_type in MessageType
        }

        logger.info("Message bus initialized")

    def register_agent(self, agent: AgentInterface):
        """
        Register an agent with the bus.

        Args:
            agent: Agent to register
        """
        self.agents[agent.agent_name] = agent
        logger.info(f"Agent '{agent.agent_name}' registered with message bus")

    def unregister_agent(self, agent_name: str):
        """
        Unregister an agent.

        Args:
            agent_name: Name of agent to unregister
        """
        if agent_name in self.agents:
            del self.agents[agent_name]
            logger.info(f"Agent '{agent_name}' unregistered from message bus")

    async def start(self):
        """Start message routing."""
        if self.running:
            return

        self.running = True

        # Start all agents
        for agent in self.agents.values():
            await agent.start()

        # Start routing task
        self.task = asyncio.create_task(self._route_messages())
        logger.info("Message bus started")

    async def stop(self):
        """Stop message routing and all agents."""
        self.running = False

        # Stop routing task
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass

        # Stop all agents
        for agent in self.agents.values():
            await agent.stop()

        logger.info("Message bus stopped")

    async def _route_messages(self):
        """Route messages from agent outboxes to recipient inboxes."""
        logger.info("Message routing started")

        while self.running:
            try:
                # Check all agent outboxes
                for agent in self.agents.values():
                    try:
                        # Non-blocking check for messages
                        message = agent.outbox.get_nowait()

                        self.total_messages += 1
                        self.messages_by_type[message.message_type] += 1

                        # Route to recipient
                        if message.recipient in self.agents:
                            recipient = self.agents[message.recipient]
                            await recipient.inbox.put((message.priority.value, message))
                        else:
                            logger.warning(f"Unknown recipient: {message.recipient}")

                    except asyncio.QueueEmpty:
                        continue

                # Small delay to prevent busy-waiting
                await asyncio.sleep(0.01)

            except asyncio.CancelledError:
                logger.info("Message routing cancelled")
                break
            except Exception as e:
                logger.error(f"Error routing messages: {e}", exc_info=True)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get message bus statistics.

        Returns:
            Statistics dictionary
        """
        return {
            'total_messages': self.total_messages,
            'messages_by_type': {
                k.value: v for k, v in self.messages_by_type.items()
            },
            'registered_agents': len(self.agents),
            'agent_stats': {
                name: agent.get_stats()
                for name, agent in self.agents.items()
            }
        }


class AgentPool:
    """
    Pool of agents for parallel task processing.

    Useful for distributing work across multiple instances of the same agent type.
    """

    def __init__(self, agent_factory: Callable[[], AgentInterface], pool_size: int = 3):
        """
        Initialize agent pool.

        Args:
            agent_factory: Factory function to create agent instances
            pool_size: Number of agents in pool
        """
        self.agent_factory = agent_factory
        self.pool_size = pool_size
        self.agents: List[AgentInterface] = []
        self.round_robin_index = 0

    async def initialize(self):
        """Initialize all agents in pool."""
        for i in range(self.pool_size):
            agent = self.agent_factory()
            agent.agent_name = f"{agent.agent_name}_{i}"
            await agent.start()
            self.agents.append(agent)

        logger.info(f"Agent pool initialized with {self.pool_size} agents")

    async def shutdown(self):
        """Shutdown all agents in pool."""
        for agent in self.agents:
            await agent.stop()

        logger.info("Agent pool shutdown complete")

    def get_next_agent(self) -> AgentInterface:
        """
        Get next agent using round-robin selection.

        Returns:
            Next available agent
        """
        agent = self.agents[self.round_robin_index]
        self.round_robin_index = (self.round_robin_index + 1) % self.pool_size
        return agent


# Example usage and testing
if __name__ == "__main__":
    from utils.logger import setup_logging

    setup_logging(level="DEBUG", console=True)

    class TestAgent(AgentInterface):
        """Test agent for demonstration."""

        async def process_task(self, data: Dict[str, Any]) -> AgentResult:
            """Process test task."""
            task_name = data.get('task', 'unknown')
            logger.info(f"Processing task: {task_name}")

            # Simulate work
            await asyncio.sleep(0.5)

            return AgentResult(
                success=True,
                data={'result': f"Completed {task_name}"},
                metadata={'processed_by': self.agent_name}
            )

    async def test_agent_system():
        """Test the agent framework."""
        print("\n" + "="*80)
        print("AGENT FRAMEWORK TEST")
        print("="*80 + "\n")

        # Create message bus
        bus = MessageBus()

        # Create agents
        agent1 = TestAgent("agent_1")
        agent2 = TestAgent("agent_2")
        agent3 = TestAgent("agent_3")

        # Register agents
        bus.register_agent(agent1)
        bus.register_agent(agent2)
        bus.register_agent(agent3)

        # Start system
        await bus.start()

        print("✓ Agent system started\n")

        # Test 1: Single request
        print("Test 1: Single request")
        result = await agent1.request(
            "agent_2",
            {'task': 'process_data'},
            timeout=5.0
        )
        print(f"  Result: {result.success}")
        print(f"  Data: {result.data}")
        print(f"  Duration: {result.duration:.3f}s\n")

        # Test 2: Multiple parallel requests
        print("Test 2: Multiple parallel requests")
        tasks = [
            agent1.request("agent_2", {'task': f'task_{i}'})
            for i in range(5)
        ]
        results = await asyncio.gather(*tasks)
        print(f"  Completed {len([r for r in results if r.success])}/{len(results)} tasks\n")

        # Test 3: Chain of requests
        print("Test 3: Chain of requests")
        result1 = await agent1.request("agent_2", {'task': 'step_1'})
        result2 = await agent2.request("agent_3", {'task': 'step_2'})
        result3 = await agent3.request("agent_1", {'task': 'step_3'})
        print(f"  Chain completed: {result1.success and result2.success and result3.success}\n")

        # Get statistics
        print("Statistics:")
        stats = bus.get_stats()
        print(f"  Total messages: {stats['total_messages']}")
        print(f"  Registered agents: {stats['registered_agents']}")

        print("\n  Agent stats:")
        for agent_name, agent_stats in stats['agent_stats'].items():
            print(f"    {agent_name}:")
            print(f"      Tasks completed: {agent_stats['tasks_completed']}")
            print(f"      Average time: {agent_stats['average_processing_time']:.3f}s")
            print(f"      Success rate: {agent_stats['success_rate']*100:.1f}%")

        # Stop system
        await bus.stop()
        print("\n✓ Agent system stopped")

        print("\n" + "="*80)
        print("TEST COMPLETE")
        print("="*80 + "\n")

    # Run test
    asyncio.run(test_agent_system())
