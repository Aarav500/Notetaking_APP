"use strict";
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};
var __param = (this && this.__param) || function (paramIndex, decorator) {
    return function (target, key) { decorator(target, key, paramIndex); }
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.AiController = void 0;
const common_1 = require("@nestjs/common");
let AiController = class AiController {
    health() {
        return { status: 'ok', mock: true, timestamp: new Date().toISOString() };
    }
    suggestions(body) {
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
};
exports.AiController = AiController;
__decorate([
    (0, common_1.Get)('health'),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", []),
    __metadata("design:returntype", void 0)
], AiController.prototype, "health", null);
__decorate([
    (0, common_1.Post)('suggestions'),
    __param(0, (0, common_1.Body)()),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [Object]),
    __metadata("design:returntype", void 0)
], AiController.prototype, "suggestions", null);
exports.AiController = AiController = __decorate([
    (0, common_1.Controller)('ai')
], AiController);
//# sourceMappingURL=ai.controller.js.map