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
exports.FlowchartsController = void 0;
const common_1 = require("@nestjs/common");
const jwt_auth_guard_1 = require("../auth/jwt-auth.guard");
const flowcharts_service_1 = require("./flowcharts.service");
const create_flowchart_dto_1 = require("./dto/create-flowchart.dto");
const update_flowchart_dto_1 = require("./dto/update-flowchart.dto");
let FlowchartsController = class FlowchartsController {
    constructor(flowchartsService) {
        this.flowchartsService = flowchartsService;
    }
    async findAll(req) {
        return this.flowchartsService.findAllByUser(req.user.userId);
    }
    async findOne(id, req) {
        return this.flowchartsService.findOneForUser(id, req.user.userId);
    }
    async create(dto, req) {
        return this.flowchartsService.createForUser(req.user.userId, dto);
    }
    async update(id, dto, req) {
        return this.flowchartsService.updateForUser(id, req.user.userId, dto);
    }
    async remove(id, req) {
        await this.flowchartsService.removeForUser(id, req.user.userId);
        return { success: true };
    }
};
exports.FlowchartsController = FlowchartsController;
__decorate([
    (0, common_1.Get)(),
    __param(0, (0, common_1.Request)()),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [Object]),
    __metadata("design:returntype", Promise)
], FlowchartsController.prototype, "findAll", null);
__decorate([
    (0, common_1.Get)(':id'),
    __param(0, (0, common_1.Param)('id', common_1.ParseIntPipe)),
    __param(1, (0, common_1.Request)()),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [Number, Object]),
    __metadata("design:returntype", Promise)
], FlowchartsController.prototype, "findOne", null);
__decorate([
    (0, common_1.Post)(),
    __param(0, (0, common_1.Body)()),
    __param(1, (0, common_1.Request)()),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [create_flowchart_dto_1.CreateFlowchartDto, Object]),
    __metadata("design:returntype", Promise)
], FlowchartsController.prototype, "create", null);
__decorate([
    (0, common_1.Put)(':id'),
    __param(0, (0, common_1.Param)('id', common_1.ParseIntPipe)),
    __param(1, (0, common_1.Body)()),
    __param(2, (0, common_1.Request)()),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [Number, update_flowchart_dto_1.UpdateFlowchartDto, Object]),
    __metadata("design:returntype", Promise)
], FlowchartsController.prototype, "update", null);
__decorate([
    (0, common_1.Delete)(':id'),
    __param(0, (0, common_1.Param)('id', common_1.ParseIntPipe)),
    __param(1, (0, common_1.Request)()),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [Number, Object]),
    __metadata("design:returntype", Promise)
], FlowchartsController.prototype, "remove", null);
exports.FlowchartsController = FlowchartsController = __decorate([
    (0, common_1.UseGuards)(jwt_auth_guard_1.JwtAuthGuard),
    (0, common_1.Controller)('flowcharts'),
    __metadata("design:paramtypes", [flowcharts_service_1.FlowchartsService])
], FlowchartsController);
//# sourceMappingURL=flowcharts.controller.js.map