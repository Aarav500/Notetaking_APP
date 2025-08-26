import { AuthService } from './auth.service';
import { RegisterDto } from './dto/register.dto';
import { LoginDto } from './dto/login.dto';
import { ForgotPasswordDto } from './dto/forgot-password.dto';
import { ResetPasswordDto } from './dto/reset-password.dto';
export declare class AuthController {
    private readonly authService;
    constructor(authService: AuthService);
    register(dto: RegisterDto): Promise<{
        user: {
            id: number;
            email: string;
            name: string;
        };
        token: string;
    }>;
    login(dto: LoginDto): Promise<{
        user: {
            id: number;
            email: string;
            name: string;
        };
        token: string;
    }>;
    forgotPassword(dto: ForgotPasswordDto): Promise<{
        message: string;
        token?: undefined;
    } | {
        message: string;
        token: string;
    }>;
    resetPassword(dto: ResetPasswordDto): Promise<{
        message: string;
    }>;
    me(req: any): Promise<{
        user: {
            id: number;
            email: string;
            name: string;
        };
    }>;
}
