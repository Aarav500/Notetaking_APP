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
exports.FlowchartsService = void 0;
const common_1 = require("@nestjs/common");
const typeorm_1 = require("@nestjs/typeorm");
const typeorm_2 = require("typeorm");
const flowchart_entity_1 = require("../entities/flowchart.entity");
let FlowchartsService = class FlowchartsService {
    constructor(flowRepo) {
        this.flowRepo = flowRepo;
    }
    async findAllByUser(userId) {
        return this.flowRepo.find({ where: { user: { id: userId } }, order: { id: 'DESC' } });
    }
    async findOneForUser(id, userId) {
        const fc = await this.flowRepo.findOne({ where: { id }, relations: ['user'] });
        if (!fc)
            throw new common_1.NotFoundException('Flowchart not found');
        if (fc.user?.id !== userId)
            throw new common_1.ForbiddenException('Access denied');
        return fc;
    }
    async createForUser(userId, dto) {
        const fc = this.flowRepo.create({ ...dto, user: { id: userId } });
        return this.flowRepo.save(fc);
    }
    async updateForUser(id, userId, dto) {
        const fc = await this.findOneForUser(id, userId);
        Object.assign(fc, dto);
        return this.flowRepo.save(fc);
    }
    async removeForUser(id, userId) {
        const fc = await this.findOneForUser(id, userId);
        await this.flowRepo.remove(fc);
    }
};
exports.FlowchartsService = FlowchartsService;
exports.FlowchartsService = FlowchartsService = __decorate([
    (0, common_1.Injectable)(),
    __param(0, (0, typeorm_1.InjectRepository)(flowchart_entity_1.Flowchart)),
    __metadata("design:paramtypes", [typeorm_2.Repository])
], FlowchartsService);
//# sourceMappingURL=flowcharts.service.js.map