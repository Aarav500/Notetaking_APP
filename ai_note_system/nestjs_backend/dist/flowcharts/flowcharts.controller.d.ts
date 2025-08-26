import { FlowchartsService } from './flowcharts.service';
import { CreateFlowchartDto } from './dto/create-flowchart.dto';
import { UpdateFlowchartDto } from './dto/update-flowchart.dto';
export declare class FlowchartsController {
    private readonly flowchartsService;
    constructor(flowchartsService: FlowchartsService);
    findAll(req: any): Promise<import("../entities/flowchart.entity").Flowchart[]>;
    findOne(id: number, req: any): Promise<import("../entities/flowchart.entity").Flowchart>;
    create(dto: CreateFlowchartDto, req: any): Promise<import("../entities/flowchart.entity").Flowchart>;
    update(id: number, dto: UpdateFlowchartDto, req: any): Promise<import("../entities/flowchart.entity").Flowchart>;
    remove(id: number, req: any): Promise<{
        success: boolean;
    }>;
}
