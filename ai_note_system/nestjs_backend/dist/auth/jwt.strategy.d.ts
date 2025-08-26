import { ConfigService } from '@nestjs/config';
export interface JwtPayload {
    sub: number;
    email: string;
}
declare const JwtStrategy_base: new (...args: any[]) => any;
export declare class JwtStrategy extends JwtStrategy_base {
    constructor(config: ConfigService);
    validate(payload: JwtPayload): Promise<{
        userId: number;
        email: string;
    }>;
}
export {};
