import { Page } from '../Main/Page'


export const AboutPage = () => (
    <Page name="О сайте">
        <h2>Описание</h2>
        <p>Сайт был разработан в рамках выполнения лабораторной работы №2
            по дисциплине «Современные платформы программирования»</p>
        <h2>Технологический стек</h2>
        <div className='tech-stack-layout'>
            <div className='tech-stack-item'>
                <h3>Frontend:</h3>
                <ul>
                    <li>React JS 18.2.0</li>
                    <li>NGiNX 1.23.1</li>
                </ul>
            </div>
            <div className='tech-stack-item'>
                <h3>Backend:</h3>
                <ul>
                    <li>Python 3.10</li>
                    <li>Aiohttp 3.8.3</li>
                </ul>
            </div>
            <div className='tech-stack-item'>
                <h3>База данных:</h3>
                PostgreSQL 14
            </div>
        </div>
    </Page>
)
