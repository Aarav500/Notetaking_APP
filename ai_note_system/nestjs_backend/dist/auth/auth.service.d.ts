import { JwtService } from '@nestjs/jwt';
import { UsersService } from '../users/users.service';
import { ConfigService } from '@nestjs/config';
export declare class AuthService {
    private readonly usersService;
    private readonly jwtService;
    private readonly configService;
    private resetTokens;
    private resetTokenTtlMs;
    constructor(usersService: UsersService, jwtService: JwtService, configService: ConfigService);
    register(email: string, password: string, name?: string): Promise<{
        user: {
            id: number;
            email: string;
            name: string;
        };
        token: string;
    }>;
    validateUser(email: string, password: string): Promise<import("../entities/user.entity").User>;
    login(email: string, password: string): Promise<{
        user: {
            id: number;
            email: string;
            name: string;
        };
        token: string;
    }>;
    me(userId: number): Promise<{
        user: {
            id: number;
            email: string;
            name: string;
        };
    }>;
    forgotPassword(email: string): Promise<{
        message: string;
        token?: undefined;
    } | {
        message: string;
        token: string;
    }>;
    resetPassword(token: string, newPassword: string): Promise<{
        message: string;
    }>;
    private signToken;
}
