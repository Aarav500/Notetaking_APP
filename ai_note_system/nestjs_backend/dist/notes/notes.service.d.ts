import { Repository } from 'typeorm';
import { Note } from '../entities/note.entity';
import { CreateNoteDto } from './dto/create-note.dto';
import { UpdateNoteDto } from './dto/update-note.dto';
export declare class NotesService {
    private readonly notesRepo;
    constructor(notesRepo: Repository<Note>);
    findAllByUser(userId: number): Promise<Note[]>;
    findOneForUser(id: number, userId: number): Promise<Note>;
    createForUser(userId: number, dto: CreateNoteDto): Promise<Note>;
    updateForUser(id: number, userId: number, dto: UpdateNoteDto): Promise<Note>;
    removeForUser(id: number, userId: number): Promise<void>;
}
