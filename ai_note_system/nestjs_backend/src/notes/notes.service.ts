import { Injectable, ForbiddenException, NotFoundException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Note } from '../entities/note.entity';
import { CreateNoteDto } from './dto/create-note.dto';
import { UpdateNoteDto } from './dto/update-note.dto';

@Injectable()
export class NotesService {
  constructor(
    @InjectRepository(Note)
    private readonly notesRepo: Repository<Note>,
  ) {}

  async findAllByUser(userId: number): Promise<Note[]> {
    return this.notesRepo.find({ where: { user: { id: userId } }, order: { id: 'DESC' } });
  }

  async findOneForUser(id: number, userId: number): Promise<Note> {
    const note = await this.notesRepo.findOne({ where: { id }, relations: ['user'] });
    if (!note) throw new NotFoundException('Note not found');
    if ((note.user as any)?.id !== userId) throw new ForbiddenException('Access denied');
    return note;
  }

  async createForUser(userId: number, dto: CreateNoteDto): Promise<Note> {
    const note = this.notesRepo.create({ ...dto, user: { id: userId } as any });
    return this.notesRepo.save(note);
  }

  async updateForUser(id: number, userId: number, dto: UpdateNoteDto): Promise<Note> {
    const note = await this.findOneForUser(id, userId);
    Object.assign(note, dto);
    return this.notesRepo.save(note);
  }

  async removeForUser(id: number, userId: number): Promise<void> {
    const note = await this.findOneForUser(id, userId);
    await this.notesRepo.remove(note);
  }
}
