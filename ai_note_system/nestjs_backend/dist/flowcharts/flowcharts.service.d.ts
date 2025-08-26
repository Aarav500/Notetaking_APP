import { Repository } from 'typeorm';
import { Flowchart } from '../entities/flowchart.entity';
import { CreateFlowchartDto } from './dto/create-flowchart.dto';
import { UpdateFlowchartDto } from './dto/update-flowchart.dto';
export declare class FlowchartsService {
    private readonly flowRepo;
    constructor(flowRepo: Repository<Flowchart>);
    findAllByUser(userId: number): Promise<Flowchart[]>;
    findOneForUser(id: number, userId: number): Promise<Flowchart>;
    createForUser(userId: number, dto: CreateFlowchartDto): Promise<Flowchart>;
    updateForUser(id: number, userId: number, dto: UpdateFlowchartDto): Promise<Flowchart>;
    removeForUser(id: number, userId: number): Promise<void>;
}
