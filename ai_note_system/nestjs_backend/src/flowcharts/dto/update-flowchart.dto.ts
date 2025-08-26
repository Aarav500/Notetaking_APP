import { IsOptional, IsString, MinLength } from 'class-validator';

export class UpdateFlowchartDto {
  @IsOptional()
  @IsString()
  @MinLength(1)
  title?: string;

  @IsOptional()
  @IsString()
  nodes?: string;

  @IsOptional()
  @IsString()
  edges?: string;
}
