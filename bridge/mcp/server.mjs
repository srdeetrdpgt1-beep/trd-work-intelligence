import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { CallToolRequestSchema, ListToolsRequestSchema } from '@modelcontextprotocol/sdk/types.js';
import { spawn } from 'node:child_process';

const server = new Server(
  {
    name: 'trd-work-intelligence-engineering-bridge',
    version: '0.1.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

const operations = [
  'RUN_TESTS',
  'GIT_STATUS',
  'GIT_DIFF',
  'CREATE_FILE',
  'UPDATE_FILE',
  'APPLY_PATCH',
  'APPLY_PATCH_AND_TEST',
];

function runBridge(task) {
  return new Promise((resolve, reject) => {
    const child = spawn(
      'python',
      ['-m', 'bridge.bridge'],
      {
        cwd: new URL('../..', import.meta.url).pathname,
        stdio: ['pipe', 'pipe', 'pipe'],
      }
    );

    let stdout = '';
    let stderr = '';

    child.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    child.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    child.on('error', reject);

    child.on('close', (code) => {
      if (code !== 0) {
        reject(
          new Error(
            stderr.trim() || `Bridge exited with code ${code}`
          )
        );
        return;
      }

      try {
        resolve(JSON.parse(stdout));
      } catch {
        reject(
          new Error(
            `Bridge returned invalid JSON: ${stdout}`
          )
        );
      }
    });

    child.stdin.write(JSON.stringify(task));
    child.stdin.end();
  });
}

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: 'submit_development_task',
      description:
        'Submit a safe allowlisted development task to the TRD Work Intelligence engineering bridge.',
      inputSchema: {
        type: 'object',
        properties: {
          task_id: {
            type: 'string',
            description: 'Unique task identifier.',
          },
          operation: {
            type: 'string',
            enum: operations,
          },
          description: {
            type: 'string',
          },
          metadata: {
            type: 'object',
            additionalProperties: true,
          },
        },
        required: ['task_id', 'operation', 'description'],
      },
    },
  ],
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name !== 'submit_development_task') {
    throw new Error(`Unknown tool: ${request.params.name}`);
  }

  const task = request.params.arguments ?? {};

  if (!operations.includes(task.operation)) {
    throw new Error(`Unsupported operation: ${task.operation}`);
  }

  const result = await runBridge(task);

  return {
    content: [
      {
        type: 'text',
        text: JSON.stringify(result, null, 2),
      },
    ],
  };
});

const transport = new StdioServerTransport();

await server.connect(transport);
