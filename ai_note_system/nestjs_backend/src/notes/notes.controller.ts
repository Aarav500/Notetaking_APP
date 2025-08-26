import { Body, Controller, Delete, Get, Param, ParseIntPipe, Post, Put, Request, UseGuards } from '@nestjs/common';
import { JwtAuthGuard } from '../auth/jwt-auth.guard';
import { NotesService } from './notes.service';
import { CreateNoteDto } from './dto/create-note.dto';
import { UpdateNoteDto } from './dto/update-note.dto';

@UseGuards(JwtAuthGuard)
@Controller('notes')
export class NotesController {
  constructor(private readonly notesService: NotesService) {}

  @Get()
  async findAll(@Request() req: any) {
    return this.notesService.findAllByUser(req.user.userId);
  }

  @Get(':id')
  async findOne(@Param('id', ParseIntPipe) id: number, @Request() req: any) {
    return this.notesService.findOneForUser(id, req.user.userId);
  }

  @Post()
  async create(@Body() dto: CreateNoteDto, @Request() req: any) {
    return this.notesService.createForUser(req.user.userId, dto);
  }

  @Put(':id')
  async update(
    @Param('id', ParseIntPipe) id: number,
    @Body() dto: UpdateNoteDto,
    @Request() req: any,
  ) {
    return this.notesService.updateForUser(id, req.user.userId, dto);
  }

  @Delete(':id')
  async remove(@Param('id', ParseIntPipe) id: number, @Request() req: any) {
    await this.notesService.removeForUser(id, req.user.userId);
    return { success: true };
  }
}
