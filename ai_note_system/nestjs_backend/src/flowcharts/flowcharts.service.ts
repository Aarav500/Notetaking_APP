import { Injectable, ForbiddenException, NotFoundException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Flowchart } from '../entities/flowchart.entity';
import { CreateFlowchartDto } from './dto/create-flowchart.dto';
import { UpdateFlowchartDto } from './dto/update-flowchart.dto';

@Injectable()
export class FlowchartsService {
  constructor(
    @InjectRepository(Flowchart)
    private readonly flowRepo: Repository<Flowchart>,
  ) {}

  async findAllByUser(userId: number): Promise<Flowchart[]> {
    return this.flowRepo.find({ where: { user: { id: userId } }, order: { id: 'DESC' } });
  }

  async findOneForUser(id: number, userId: number): Promise<Flowchart> {
    const fc = await this.flowRepo.findOne({ where: { id }, relations: ['user'] });
    if (!fc) throw new NotFoundException('Flowchart not found');
    if ((fc.user as any)?.id !== userId) throw new ForbiddenException('Access denied');
    return fc;
  }

  async createForUser(userId: number, dto: CreateFlowchartDto): Promise<Flowchart> {
    const fc = this.flowRepo.create({ ...dto, user: { id: userId } as any });
    return this.flowRepo.save(fc);
  }

  async updateForUser(id: number, userId: number, dto: UpdateFlowchartDto): Promise<Flowchart> {
    const fc = await this.findOneForUser(id, userId);
    Object.assign(fc, dto);
    return this.flowRepo.save(fc);
  }

  async removeForUser(id: number, userId: number): Promise<void> {
    const fc = await this.findOneForUser(id, userId);
    await this.flowRepo.remove(fc);
  }
}
