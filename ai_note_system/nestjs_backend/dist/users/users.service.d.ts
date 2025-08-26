import { Repository } from 'typeorm';
import { User } from '../entities/user.entity';
export declare class UsersService {
    private readonly usersRepo;
    constructor(usersRepo: Repository<User>);
    create(email: string, password: string, name?: string): Promise<User>;
    findByEmail(email: string): Promise<User | null>;
    findById(id: number): Promise<User>;
    updatePassword(id: number, newPassword: string): Promise<void>;
}
