import { Injectable, UnauthorizedException, BadRequestException } from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import { UsersService } from '../users/users.service';
import * as bcrypt from 'bcrypt';
import { ConfigService } from '@nestjs/config';
import * as crypto from 'crypto';

interface ResetTokenRecord {
  userId: number;
  expiresAt: number;
}

@Injectable()
export class AuthService {
  private resetTokens = new Map<string, ResetTokenRecord>();
  private resetTokenTtlMs: number;

  constructor(
    private readonly usersService: UsersService,
    private readonly jwtService: JwtService,
    private readonly configService: ConfigService,
  ) {
    this.resetTokenTtlMs = this.configService.get<number>('RESET_TOKEN_TTL_MS') || 15 * 60 * 1000; // 15 min
  }

  async register(email: string, password: string, name?: string) {
    const user = await this.usersService.create(email, password, name);
    const token = await this.signToken(user.id, user.email);
    return { user: { id: user.id, email: user.email, name: user.name }, token };
  }

  async validateUser(email: string, password: string) {
    const user = await this.usersService.findByEmail(email);
    if (!user) throw new UnauthorizedException('Invalid credentials');
    const match = await bcrypt.compare(password, user.password);
    if (!match) throw new UnauthorizedException('Invalid credentials');
    return user;
  }

  async login(email: string, password: string) {
    const user = await this.validateUser(email, password);
    const token = await this.signToken(user.id, user.email);
    return { user: { id: user.id, email: user.email, name: user.name }, token };
  }

  async me(userId: number) {
    const user = await this.usersService.findById(userId);
    return { user: { id: user.id, email: user.email, name: user.name } };
  }

  async forgotPassword(email: string) {
    const user = await this.usersService.findByEmail(email);
    if (!user) {
      // For security, do not reveal if user exists
      return { message: 'If the email exists, a reset link has been sent.' };
    }
    const token = crypto.randomBytes(24).toString('hex');
    const expiresAt = Date.now() + this.resetTokenTtlMs;
    this.resetTokens.set(token, { userId: user.id, expiresAt });
    // In a real system, email the token link. Here we just return it for testing.
    return { message: 'Reset token generated', token };
  }

  async resetPassword(token: string, newPassword: string) {
    const entry = this.resetTokens.get(token);
    if (!entry) throw new BadRequestException('Invalid or expired token');
    if (Date.now() > entry.expiresAt) {
      this.resetTokens.delete(token);
      throw new BadRequestException('Invalid or expired token');
    }
    await this.usersService.updatePassword(entry.userId, newPassword);
    this.resetTokens.delete(token);
    return { message: 'Password reset successful' };
  }

  private async signToken(userId: number, email: string): Promise<string> {
    return this.jwtService.signAsync({ sub: userId, email });
  }
}