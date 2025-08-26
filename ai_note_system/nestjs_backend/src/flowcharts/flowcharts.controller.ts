import { Body, Controller, Delete, Get, Param, ParseIntPipe, Post, Put, Request, UseGuards } from '@nestjs/common';
import { JwtAuthGuard } from '../auth/jwt-auth.guard';
import { FlowchartsService } from './flowcharts.service';
import { CreateFlowchartDto } from './dto/create-flowchart.dto';
import { UpdateFlowchartDto } from './dto/update-flowchart.dto';

@UseGuards(JwtAuthGuard)
@Controller('flowcharts')
export class FlowchartsController {
  constructor(private readonly flowchartsService: FlowchartsService) {}

  @Get()
  async findAll(@Request() req: any) {
    return this.flowchartsService.findAllByUser(req.user.userId);
  }

  @Get(':id')
  async findOne(@Param('id', ParseIntPipe) id: number, @Request() req: any) {
    return this.flowchartsService.findOneForUser(id, req.user.userId);
  }

  @Post()
  async create(@Body() dto: CreateFlowchartDto, @Request() req: any) {
    return this.flowchartsService.createForUser(req.user.userId, dto);
  }

  @Put(':id')
  async update(
    @Param('id', ParseIntPipe) id: number,
    @Body() dto: UpdateFlowchartDto,
    @Request() req: any,
  ) {
    return this.flowchartsService.updateForUser(id, req.user.userId, dto);
  }

  @Delete(':id')
  async remove(@Param('id', ParseIntPipe) id: number, @Request() req: any) {
    await this.flowchartsService.removeForUser(id, req.user.userId);
    return { success: true };
  }
}
