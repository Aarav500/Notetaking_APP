import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { Flowchart } from '../entities/flowchart.entity';
import { FlowchartsService } from './flowcharts.service';
import { FlowchartsController } from './flowcharts.controller';

@Module({
  imports: [TypeOrmModule.forFeature([Flowchart])],
  controllers: [FlowchartsController],
  providers: [FlowchartsService],
  exports: [FlowchartsService],
})
export class FlowchartsModule {}
