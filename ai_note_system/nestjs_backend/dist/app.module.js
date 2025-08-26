"use strict";
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.AppModule = void 0;
const common_1 = require("@nestjs/common");
const typeorm_1 = require("@nestjs/typeorm");
const config_1 = require("@nestjs/config");
const users_module_1 = require("./users/users.module");
const auth_module_1 = require("./auth/auth.module");
const notes_module_1 = require("./notes/notes.module");
const flowcharts_module_1 = require("./flowcharts/flowcharts.module");
const ai_module_1 = require("./ai/ai.module");
let AppModule = class AppModule {
};
exports.AppModule = AppModule;
exports.AppModule = AppModule = __decorate([
    (0, common_1.Module)({
        imports: [
            config_1.ConfigModule.forRoot({
                isGlobal: true,
            }),
            typeorm_1.TypeOrmModule.forRootAsync({
                imports: [config_1.ConfigModule],
                inject: [config_1.ConfigService],
                useFactory: (config) => {
                    const dbType = (config.get('DB_TYPE') || 'sqlite').toLowerCase();
                    const synchronize = (config.get('DB_SYNCHRONIZE') || 'true') === 'true';
                    if (dbType === 'oracle') {
                        return {
                            type: 'oracle',
                            host: config.get('DB_HOST', 'localhost'),
                            port: config.get('DB_PORT', 1521),
                            username: config.get('DB_USERNAME', 'admin'),
                            password: config.get('DB_PASSWORD', 'password'),
                            sid: config.get('DB_SID', 'ORCLCDB'),
                            autoLoadEntities: true,
                            synchronize,
                        };
                    }
                    if (dbType === 'postgres' || dbType === 'postgresql' || dbType === 'pg') {
                        return {
                            type: 'postgres',
                            host: config.get('DB_HOST', 'localhost'),
                            port: config.get('DB_PORT', 5432),
                            username: config.get('DB_USERNAME', 'postgres'),
                            password: config.get('DB_PASSWORD', 'postgres'),
                            database: config.get('DB_NAME', 'ai_notes'),
                            autoLoadEntities: true,
                            synchronize,
                        };
                    }
                    return {
                        type: 'sqlite',
                        database: config.get('SQLITE_DB', 'dev.sqlite'),
                        autoLoadEntities: true,
                        synchronize,
                    };
                },
            }),
            users_module_1.UsersModule,
            auth_module_1.AuthModule,
            notes_module_1.NotesModule,
            flowcharts_module_1.FlowchartsModule,
            ai_module_1.AiModule,
        ],
        controllers: [],
        providers: [],
    })
], AppModule);
//# sourceMappingURL=app.module.js.map