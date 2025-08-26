import { Test, TestingModule } from '@nestjs/testing';
import { FlowchartsService } from './flowcharts.service';
import { Repository } from 'typeorm';
import { Flowchart } from '../entities/flowchart.entity';
import { getRepositoryToken } from '@nestjs/typeorm';
import { ForbiddenException, NotFoundException } from '@nestjs/common';

const repoMock = () => ({
  find: jest.fn(),
  findOne: jest.fn(),
  create: jest.fn(),
  save: jest.fn(),
  remove: jest.fn(),
});

describe('FlowchartsService', () => {
  let service: FlowchartsService;
  let repo: jest.Mocked<Repository<Flowchart>>;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        FlowchartsService,
        { provide: getRepositoryToken(Flowchart), useFactory: repoMock },
      ],
    }).compile();

    service = module.get<FlowchartsService>(FlowchartsService);
    repo = module.get(getRepositoryToken(Flowchart));
  });

  it('findAllByUser should query user scoped flowcharts', async () => {
    repo.find.mockResolvedValue([{ id: 1 } as any]);
    const res = await service.findAllByUser(10);
    expect(repo.find).toHaveBeenCalledWith({ where: { user: { id: 10 } }, order: { id: 'DESC' } });
    expect(res).toHaveLength(1);
  });

  it('findOneForUser returns owned flowchart', async () => {
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

  it('createForUser creates and saves flowchart', async () => {
    const dto = { title: 't', nodes: '[]', edges: '[]' } as any;
    repo.create.mockReturnValue({ id: 3, ...dto } as any);
    repo.save.mockResolvedValue({ id: 3, ...dto } as any);
    const res = await service.createForUser(10, dto);
    expect(repo.create).toHaveBeenCalledWith({ ...dto, user: { id: 10 } as any });
    expect(res.id).toBe(3);
  });

  it('updateForUser merges and saves', async () => {
    const existing = { id: 4, title: 'old', nodes: '[]', edges: '[]', user: { id: 10 } } as any;
    repo.findOne.mockResolvedValue(existing);
    repo.save.mockImplementation(async (e: any) => e);
    const res = await service.updateForUser(4, 10, { title: 'new' } as any);
    expect(res.title).toBe('new');
  });

  it('removeForUser removes flowchart', async () => {
    const existing = { id: 5, user: { id: 10 } } as any;
    repo.findOne.mockResolvedValue(existing);
    await service.removeForUser(5, 10);
    expect(repo.remove).toHaveBeenCalledWith(existing);
  });
});
