import { NotesService } from './notes.service';
import { CreateNoteDto } from './dto/create-note.dto';
import { UpdateNoteDto } from './dto/update-note.dto';
export declare class NotesController {
    private readonly notesService;
    constructor(notesService: NotesService);
    findAll(req: any): Promise<import("../entities/note.entity").Note[]>;
    findOne(id: number, req: any): Promise<import("../entities/note.entity").Note>;
    create(dto: CreateNoteDto, req: any): Promise<import("../entities/note.entity").Note>;
    update(id: number, dto: UpdateNoteDto, req: any): Promise<import("../entities/note.entity").Note>;
    remove(id: number, req: any): Promise<{
        success: boolean;
    }>;
}
