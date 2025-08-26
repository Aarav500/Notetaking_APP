import { Test, TestingModule } from '@nestjs/testing';
import { NotesService } from './notes.service';
import { Repository } from 'typeorm';
import { Note } from '../entities/note.entity';
import { getRepositoryToken } from '@nestjs/typeorm';
import { ForbiddenException, NotFoundException } from '@nestjs/common';

const repoMock = () => ({
  find: jest.fn(),
  findOne: jest.fn(),
  create: jest.fn(),
  save: jest.fn(),
  remove: jest.fn(),
});

describe('NotesService', () => {
  let service: NotesService;
  let repo: jest.Mocked<Repository<Note>>;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        NotesService,
        { provide: getRepositoryToken(Note), useFactory: repoMock },
      ],
    }).compile();

    service = module.get<NotesService>(NotesService);
    repo = module.get(getRepositoryToken(Note));
  });

  it('findAllByUser should query user scoped notes', async () => {
    repo.find.mockResolvedValue([{ id: 1 } as any]);
    const res = await service.findAllByUser(10);
    expect(repo.find).toHaveBeenCalledWith({ where: { user: { id: 10 } }, order: { id: 'DESC' } });
    expect(res).toHaveLength(1);
  });

  it('findOneForUser returns owned note', async () => {
    repo.findOne.mockResolvedValue({ id: 2, user: { id: 10 } } as any);
    const res = await service.findOneForUser(2, 10);
    expect(res.id).toBe(2);
  });

  it('findOneForUser throws NotFound if missing', async () => {
    repo.findOne.mockResolvedValue(null);
    await expect(service.findOneForUser(99, 10)).rejects.toBeInstanceOf(NotFoundException);
  });

  it('findOneForUser throws Forbidden if not owner', async () => {
    repo.findOne.mockResolvedValue({ id: 2, user: { id: 999 } } as any);
    await expect(service.findOneForUser(2, 10)).rejects.toBeInstanceOf(ForbiddenException);
  });

  it('createForUser creates and saves note', async () => {
    const dto = { title: 't', content: 'c' } as any;
    repo.create.mockReturnValue({ id: 3, ...dto } as any);
    repo.save.mockResolvedValue({ id: 3, ...dto } as any);
    const res = await service.createForUser(10, dto);
    expect(repo.create).toHaveBeenCalledWith({ ...dto, user: { id: 10 } as any });
    expect(res.id).toBe(3);
  });

  it('updateForUser merges and saves', async () => {
    const existing = { id: 4, title: 'old', content: 'x', user: { id: 10 } } as any;
    repo.findOne.mockResolvedValue(existing);
    repo.save.mockImplementation(async (e: any) => e);
    const res = await service.updateForUser(4, 10, { title: 'new' } as any);
    expect(res.title).toBe('new');
  });

  it('removeForUser removes note', async () => {
    const existing = { id: 5, user: { id: 10 } } as any;
    repo.findOne.mockResolvedValue(existing);
    await service.removeForUser(5, 10);
    expect(repo.remove).toHaveBeenCalledWith(existing);
  });
});
