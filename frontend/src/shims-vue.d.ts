/// <reference types="vite/client" />

declare module '*.vue' {
    import type { DefineComponent } from 'vue'
    const component: DefineComponent<{}, {}, any>
    export default component
}

declare module '@element-plus/icons-vue' {
    import type { Component } from 'vue'
    const component: Component
    export const VideoCamera: Component
    export const VideoPlay: Component
    export const VideoPause: Component
    export const Camera: Component
    export const Search: Component
    export const User: Component
    export const Upload: Component
    export const Document: Component
}

declare module 'element-plus'
declare module 'axios' 