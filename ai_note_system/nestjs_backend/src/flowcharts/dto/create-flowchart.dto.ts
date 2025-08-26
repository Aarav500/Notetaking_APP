import { IsString, MinLength } from 'class-validator';

export class CreateFlowchartDto {
  @IsString()
  @MinLength(1)
  title: string;

  // Serialized JSON strings
  @IsString()
  nodes: string;

  @IsString()
  edges: string;
}
