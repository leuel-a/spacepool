import type {Route} from './+types/home';
import {Welcome} from '@/components/pages/Home/Welcome';

export function meta({}: Route.MetaArgs) {
    return [
        {title: 'spacepool'},
        {name: 'description', content: 'Welcome to spacepool!'},
    ];
}

export default function Home() {
    return <Welcome />;
}
