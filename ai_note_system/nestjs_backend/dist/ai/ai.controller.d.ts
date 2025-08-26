export declare class AiController {
    health(): {
        status: string;
        mock: boolean;
        timestamp: string;
    };
    suggestions(body: any): {
        type: any;
        suggestions: string[];
        sample: {
            title: any;
            nodes: string;
            edges: string;
            content?: undefined;
            is_ai_generated?: undefined;
        };
    } | {
        type: string;
        suggestions: string[];
        sample: {
            title: any;
            content: string;
            is_ai_generated: boolean;
            nodes?: undefined;
            edges?: undefined;
        };
    };
}
