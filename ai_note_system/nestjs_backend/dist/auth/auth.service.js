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
Object.defineProperty(exports, "__esModule", { value: true });
exports.AuthService = void 0;
const common_1 = require("@nestjs/common");
const jwt_1 = require("@nestjs/jwt");
const users_service_1 = require("../users/users.service");
const bcrypt = require("bcrypt");
const config_1 = require("@nestjs/config");
const crypto = require("crypto");
let AuthService = class AuthService {
    constructor(usersService, jwtService, configService) {
        this.usersService = usersService;
        this.jwtService = jwtService;
        this.configService = configService;
        this.resetTokens = new Map();
        this.resetTokenTtlMs = this.configService.get('RESET_TOKEN_TTL_MS') || 15 * 60 * 1000;
    }
    async register(email, password, name) {
        const user = await this.usersService.create(email, password, name);
        const token = await this.signToken(user.id, user.email);
        return { user: { id: user.id, email: user.email, name: user.name }, token };
    }
    async validateUser(email, password) {
        const user = await this.usersService.findByEmail(email);
        if (!user)
            throw new common_1.UnauthorizedException('Invalid credentials');
        const match = await bcrypt.compare(password, user.password);
        if (!match)
            throw new common_1.UnauthorizedException('Invalid credentials');
        return user;
    }
    async login(email, password) {
        const user = await this.validateUser(email, password);
        const token = await this.signToken(user.id, user.email);
        return { user: { id: user.id, email: user.email, name: user.name }, token };
    }
    async me(userId) {
        const user = await this.usersService.findById(userId);
        return { user: { id: user.id, email: user.email, name: user.name } };
    }
    async forgotPassword(email) {
        const user = await this.usersService.findByEmail(email);
        if (!user) {
            return { message: 'If the email exists, a reset link has been sent.' };
        }
        const token = crypto.randomBytes(24).toString('hex');
        const expiresAt = Date.now() + this.resetTokenTtlMs;
        this.resetTokens.set(token, { userId: user.id, expiresAt });
        return { message: 'Reset token generated', token };
    }
    async resetPassword(token, newPassword) {
        const entry = this.resetTokens.get(token);
        if (!entry)
            throw new common_1.BadRequestException('Invalid or expired token');
        if (Date.now() > entry.expiresAt) {
            this.resetTokens.delete(token);
            throw new common_1.BadRequestException('Invalid or expired token');
        }
        await this.usersService.updatePassword(entry.userId, newPassword);
        this.resetTokens.delete(token);
        return { message: 'Password reset successful' };
    }
    async signToken(userId, email) {
        return this.jwtService.signAsync({ sub: userId, email });
    }
};
exports.AuthService = AuthService;
exports.AuthService = AuthService = __decorate([
    (0, common_1.Injectable)(),
    __metadata("design:paramtypes", [users_service_1.UsersService,
        jwt_1.JwtService,
        config_1.ConfigService])
], AuthService);
//# sourceMappingURL=auth.service.js.map