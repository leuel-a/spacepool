import path from 'path';
import {defineConfig} from 'vite';
import {reactRouter} from '@react-router/dev/vite';
import react, {reactCompilerPreset} from '@vitejs/plugin-react';
import babel from '@rolldown/plugin-babel';
import tailwindcss from '@tailwindcss/vite';

// https://vite.dev/config/
export default defineConfig({
    plugins: [
        react(),
        babel({presets: [reactCompilerPreset()]}),
        tailwindcss(),
        reactRouter(),
    ],
    resolve: {
        alias: {
            '@': path.resolve(__dirname, './app'),
        },
    },
    server: {port: 3000},
});
