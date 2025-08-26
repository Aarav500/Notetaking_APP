import { Body, Controller, Get, Post } from '@nestjs/common';

@Controller('ai')
export class AiController {
  @Get('health')
  health() {
    return { status: 'ok', mock: true, timestamp: new Date().toISOString() };
  }

  @Post('suggestions')
  suggestions(@Body() body: any) {
    const type = (body?.type || 'note').toLowerCase();

    if (type === 'flowchart') {
      return {
        type,
        suggestions: [
          'Start with a clear entry node (Start).',
          'Break the process into small, well-named steps.',
          'Use Decision nodes to branch logic clearly.',
          'Ensure every path ultimately leads to an End node.',
        ],
        sample: {
          title: body?.title || 'Sample Flow',
          nodes: JSON.stringify([
            { id: 'start', label: 'Start' },
            { id: 'p1', label: 'Process' },
            { id: 'd1', label: 'Decision' },
            { id: 'end', label: 'End' },
          ]),
          edges: JSON.stringify([
            { from: 'start', to: 'p1' },
            { from: 'p1', to: 'd1' },
            { from: 'd1', to: 'end' },
          ]),
        },
      };
    }

    return {
      type: 'note',
      suggestions: [
        'Create an outline: Introduction, Main Points, Conclusion.',
        'Use bullet points for clarity and brevity.',
        'Add action items with clear owners and deadlines.',
        'Summarize the key takeaways at the end.',
      ],
      sample: {
        title: body?.title || 'Sample Note',
        content: '- Introduction\n- Key Points\n- Action Items',
        is_ai_generated: true,
      },
    };
  }
}
