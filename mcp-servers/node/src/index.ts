/**
 * MCP Server - Node.js Example
 * AI Testing 项目的 MCP 服务端 Node.js 实现
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
} from "@modelcontextprotocol/sdk/types.js";

const TOOLS: Tool[] = [
  {
    name: "calculator",
    description: "Perform mathematical calculations",
    inputSchema: {
      type: "object",
      properties: {
        expression: { type: "string", description: "Math expression like '2 + 2'" },
      },
      required: ["expression"],
    },
  },
  {
    name: "echo",
    description: "Echo back input for testing",
    inputSchema: {
      type: "object",
      properties: {
        message: { type: "string", description: "Message to echo" },
      },
      required: ["message"],
    },
  },
];

const server = new Server(
  { name: "ai-test-server", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({ tools: TOOLS }));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  
  if (name === "calculator") {
    try {
      const result = Function('"use strict"; return (' + args.expression + ')')();
      return { content: [{ type: "text", text: String(result) }] };
    } catch (e: any) {
      return { content: [{ type: "text", text: `Error: ${e.message}` }] };
    }
  }
  
  if (name === "echo") {
    return { content: [{ type: "text", text: `Echo: ${args.message}` }] };
  }
  
  throw new Error(`Unknown tool: ${name}`);
});

const transport = new StdioServerTransport();
await server.connect(transport);
console.error("MCP Node.js Server running on stdio");
