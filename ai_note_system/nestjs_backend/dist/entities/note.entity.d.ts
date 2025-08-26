import { User } from './user.entity';
export declare class Note {
    id: number;
    title: string;
    content: string;
    is_ai_generated: boolean;
    user: User;
}
