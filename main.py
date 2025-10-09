import threading
import time
import requests
from bs4 import BeautifulSoup
import random
import string
import json
from queue import Queue
import os
from collections import deque
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn, SpinnerColumn
from rich.text import Text
from rich.layout import Layout
from rich.live import Live
import pyfiglet

console = Console()

class ConsoleColor:
    HEADER, OKGREEN, FAIL, WARNING, OKBLUE = 'bold cyan', 'bold green', 'bold red', 'yellow', 'bold blue'

log_lock = threading.Lock()
live_logs = deque(maxlen=10)

class Target:
    def __init__(self, url, target_id):
        self.id = target_id
        self.url = url
        self.view_url = None
        self.post_url = None
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"})
        self.questions_by_page = []
        self.page_count = 0
        self.initial_fbzx = None
        self.successful_requests = 0
        self.failed_requests = 0
        self.status = "Aguardando Análise"
        self.progress_task_id = None
        self.lock = threading.Lock()
        self.custom_answers = {}

    def is_complete(self, desired_successes):
        return self.successful_requests >= desired_successes or self.status.startswith("Erro")

    def analyze(self):
        try:
            self.status = "Analisando..."
            response = self.session.get(self.url, allow_redirects=True, timeout=15)
            self.view_url = response.url
            if "/viewform" not in self.view_url: raise ValueError("Link inválido")
            self.questions_by_page, self.page_count = scrape_form_structure(response.text)
            if not any(self.questions_by_page): raise ValueError("Não encontrou perguntas")
            soup = BeautifulSoup(response.text, 'html.parser')
            self.initial_fbzx = soup.find('input', {'name': 'fbzx'})['value'] if soup.find('input', {'name': 'fbzx'}) else None
            if not self.initial_fbzx: raise ValueError("Não encontrou token fbzx")
            self.post_url = self.view_url.replace("/viewform", "/formResponse")
            self.session.headers.update({"Referer": self.view_url})
            self.status = "Pronto para Envio"
            return True
        except Exception as e:
            self.status = f"Erro na Análise: {e}"
            return False

PROXY_SOURCES = ["https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all", "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt"]
TEST_URL, PROXY_TIMEOUT = 'https://www.google.com', 7

def test_proxy_worker(q, good_proxy_list, bad_proxy_logs, total_bad_proxies, progress, task_id):
    while not q.empty():
        proxy = q.get()
        try:
            proxy_dict = {'http': f'http://{proxy}', 'https': f'http://{proxy}'}
            requests.get(TEST_URL, proxies=proxy_dict, timeout=PROXY_TIMEOUT)
            with log_lock:
                good_proxy_list.append(proxy)
                progress.update(task_id, description=f"[green]{len(good_proxy_list)} aprovados[/green]")
        except Exception:
            with log_lock:
                bad_proxy_logs.append(proxy)
                total_bad_proxies[0] += 1
        finally:
            with log_lock: progress.update(task_id, advance=1)
            q.task_done()

def setup_proxy_test(good_proxy_logs, bad_proxy_logs, total_bad_proxies):
    raw_proxies = set()
    with console.status("[bold green]Baixando listas de proxies...", spinner="earth"):
        for url in PROXY_SOURCES:
            try:
                response = requests.get(url, timeout=10)
                proxies_from_source = {p.strip() for p in response.text.strip().split('\n') if p.strip()}
                raw_proxies.update(proxies_from_source)
            except Exception: pass
    if not raw_proxies: return None, None, None
    q = Queue(); [q.put(p) for p in raw_proxies]
    progress_proxies = Progress(SpinnerColumn(), TextColumn("[bold blue]Testando {task.total} proxies..."), BarColumn(), "[progress.percentage]{task.percentage:>3.0f}%", "•", TextColumn("{task.description}"), TimeRemainingColumn())
    task_id = progress_proxies.add_task(description="[green]0 aprovados[/green]", total=len(raw_proxies))
    threads = [threading.Thread(target=test_proxy_worker, args=(q, good_proxy_logs, bad_proxy_logs, total_bad_proxies, progress_proxies, task_id)) for _ in range(min(200, len(raw_proxies)))]
    for t in threads: t.start()
    return progress_proxies, q, good_proxy_logs

def get_random_string(length=10): return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def generate_answers(questions_by_page, custom_answers={}):
    page_answers = []
    for page in questions_by_page:
        answers = {}
        for q in page:
            q_id, q_type, options, title = q.get('id'), q.get('type'), q.get('options'), q.get('title')
            
            if q_id in custom_answers:
                answers[q_id] = custom_answers[q_id]
                continue

            if not q_id: continue
            if "texto" in q_type: answers[q_id] = get_random_string()
            elif q_type in ["multipla_escolha", "lista_suspensa", "escala_linear", "classificacao"]:
                if options: answers[q_id] = random.choice(options)
            elif q_type == "caixas_selecao":
                if options: answers[q_id] = random.sample(options, k=random.randint(1, len(options)))
            elif q_type == "data":
                answers[f"{q_id}_year"], answers[f"{q_id}_month"], answers[f"{q_id}_day"] = str(random.randint(2000, 2024)), str(random.randint(1, 12)), str(random.randint(1, 28))
            elif q_type == "hora":
                answers[f"{q_id}_hour"], answers[f"{q_id}_minute"] = str(random.randint(0, 23)), str(random.randint(0, 59))
            elif q_type == "grade_multipla_escolha":
                for row_id, row_options in options.items():
                    if row_options: answers[row_id] = random.choice(row_options)
            elif q_type == "grade_caixa_selecao":
                for row_id, row_options in options.items():
                    if row_options:
                        if (num_to_select := random.randint(0, len(row_options))) > 0: answers[row_id] = random.sample(row_options, num_to_select)
        page_answers.append(answers)
    return page_answers

def scrape_form_structure(html):
    soup = BeautifulSoup(html, 'html.parser')
    script_tag = soup.find('script', string=lambda t: t and 'FB_PUBLIC_LOAD_DATA_' in t)
    if not script_tag: return [], 0
    json_str = script_tag.string.replace('var FB_PUBLIC_LOAD_DATA_ = ', '').rstrip(';')
    data = json.loads(json_str)
    question_list = data[1][1] if len(data) > 1 and len(data[1]) > 1 and data[1][1] else []
    if not question_list: return [], 0
    page_break_code = 8
    num_page_breaks = sum(1 for q_data in question_list if len(q_data) > 3 and q_data[3] == page_break_code)
    page_count = num_page_breaks + 1
    questions_by_page = [[] for _ in range(page_count)]
    current_page_index = 0
    for q_data in question_list:
        try:
            q_type_code = q_data[3]
            if q_type_code == page_break_code: current_page_index += 1; continue
            if current_page_index >= page_count: continue
            question_info, q_id_data = {}, q_data[4][0]
            question_info['title'] = q_data[1] if q_data[1] else "Pergunta sem título"
            question_info['id'] = f"entry.{q_id_data[0]}"
            question_info['options'] = [opt[0] for opt in q_id_data[1] if opt and opt[0]] if q_id_data[1] else []
            if q_type_code in [0, 1]: question_info['type'] = "texto"
            elif q_type_code == 2: question_info['type'] = "multipla_escolha"
            elif q_type_code == 3: question_info['type'] = "lista_suspensa"
            elif q_type_code == 4: question_info['type'] = "caixas_selecao"
            elif q_type_code == 5: question_info['type'] = "escala_linear"
            elif q_type_code == 18: question_info['type'] = "classificacao"
            elif q_type_code == 9: question_info['type'] = "data"
            elif q_type_code == 10: question_info['type'] = "hora"
            elif q_type_code == 7:
                is_checkbox_grid = len(q_id_data) > 7 and q_id_data[7]
                question_info['type'] = "grade_caixa_selecao" if is_checkbox_grid else "grade_multipla_escolha"
                question_info['options'] = {f"entry.{r[0]}": [c[0] for c in r[1] if c[0]] for r in q_data[4]}
            else: continue
            questions_by_page[current_page_index].append(question_info)
        except (TypeError, IndexError): continue
    return questions_by_page, page_count

def do_request(target, delay, proxy_list):
    try:
        thread_id = threading.get_ident() % 1000
        if delay > 0: time.sleep(delay)
        proxy_dict = {'http': f'http://{p}', 'https': f'http://{p}'} if proxy_list and (p := random.choice(proxy_list)) else None
        
        all_answers = generate_answers(target.questions_by_page, target.custom_answers)
        accumulated_answers, current_fbzx = {}, target.initial_fbzx
        
        for page_index, page_answers in enumerate(all_answers):
            accumulated_answers.update(page_answers)
            is_last_page = (page_index == len(all_answers) - 1)
            payload = {**accumulated_answers, "fvv": "1", "pageHistory": ",".join(map(str, range(page_index + 1))), "submissionTimestamp": int(time.time() * 1000)}
            if current_fbzx: payload['fbzx'], payload['draftResponse'] = current_fbzx, f'[null,null,"{current_fbzx}"]'
            if not is_last_page: payload['continue'] = '1'
            response = target.session.post(target.post_url, data=payload, proxies=proxy_dict, timeout=15)
            if is_last_page:
                if "Sua resposta foi registrada" in response.text or "Your response has been recorded" in response.text:
                    with target.lock: target.successful_requests += 1
                    with log_lock: live_logs.append(f"[green][Alvo {target.id}] T{thread_id}: Sucesso![/green]")
                else: raise Exception("Falha no envio final")
            else:
                soup = BeautifulSoup(response.text, 'html.parser')
                fbzx_input = soup.find('input', {'name': 'fbzx'})
                if not fbzx_input or not fbzx_input.get('value'): raise Exception(f"Não encontrou fbzx pág. {page_index + 2}")
                current_fbzx = fbzx_input['value']
    except Exception as e:
        with target.lock: target.failed_requests += 1
        with log_lock: live_logs.append(f"[red][Alvo {target.id}] T{thread_id}: Falhou - {e}[/red]")

def make_layout():
    layout = Layout(name="root")
    layout.split(Layout(name="header", size=8), Layout(name="main", ratio=1))
    layout["main"].split(Layout(name="body", ratio=1), Layout(name="footer", size=12))
    layout["body"].split_row(Layout(name="side", minimum_size=45), Layout(name="content", ratio=2))
    return layout

def get_custom_answers(target):
    console.print(Panel(f"Respostas Customizadas para o Alvo #{target.id}: {target.url[:60]}...", border_style="magenta"))
    if console.input(f"  [{ConsoleColor.OKBLUE}]Deseja definir respostas fixas para este formulário? (s/n):[/] ").lower() != 's':
        return

    for i, page in enumerate(target.questions_by_page):
        console.print(f"\n--- Página {i+1} ---")
        for q in page:
            console.print(Panel(f"[yellow]Pergunta:[/] {q['title']}"))
            q_id, q_type, options = q.get('id'), q.get('type'), q.get('options')
            
            if q_type == "texto":
                answer = console.input("  [cyan]Resposta (deixe em branco para aleatório):[/] ")
                if answer: target.custom_answers[q_id] = answer

            elif q_type in ["multipla_escolha", "lista_suspensa"]:
                for idx, opt in enumerate(options): console.print(f"    [dim][{idx+1}][/dim] {opt}")
                choice = console.input("  [cyan]Escolha uma opção pelo número (deixe em branco para aleatório):[/] ")
                try:
                    if choice and 0 < int(choice) <= len(options):
                        target.custom_answers[q_id] = options[int(choice)-1]
                except ValueError:
                    console.print("[red]Entrada inválida. A pergunta será aleatória.[/red]")

            elif q_type == "caixas_selecao":
                for idx, opt in enumerate(options): console.print(f"    [dim][{idx+1}][/dim] {opt}")
                choices_str = console.input("  [cyan]Escolha as opções (números separados por vírgula, ex: 1,3):[/] ")
                if choices_str:
                    try:
                        selected_options = []
                        indices = [int(i.strip()) for i in choices_str.split(',')]
                        for idx in indices:
                            if 0 < idx <= len(options):
                                selected_options.append(options[idx-1])
                        if selected_options:
                            target.custom_answers[q_id] = selected_options
                    except ValueError:
                        console.print("[red]Entrada inválida. A pergunta será aleatória.[/red]")

def get_user_input():
    console.print(Panel(f"[{ConsoleColor.HEADER}]Por favor, insira as informações abaixo[/]", border_style="cyan"))
    urls = []
    while True:
        url = console.input(f"  [{ConsoleColor.OKBLUE}]URL do Form #{len(urls) + 1} (ou deixe em branco para continuar):[/] ")
        if not url:
            if not urls: console.print("[red]Você precisa adicionar pelo menos uma URL.[/red]"); continue
            break
        urls.append(url)
    use_proxies = console.input(f"  [{ConsoleColor.OKBLUE}]Deseja usar proxies? (s/n):[/] ").lower() == 's'
    delay = float(console.input(f"  [{ConsoleColor.OKBLUE}]Delay entre envios (ex: 0.1):[/] "))
    desired_successes = int(console.input(f"  [{ConsoleColor.OKBLUE}]Quantos envios BEM-SUCEDIDOS por link?:[/] "))
    concurrent_threads = int(console.input(f"  [{ConsoleColor.OKBLUE}]Quantos envios simultâneos (threads TOTAIS)?:[/] "))
    return urls, use_proxies, delay, desired_successes, concurrent_threads

def main():
    while True:
        live_logs.clear()
        os.system('cls' if os.name == 'nt' else 'clear')
        urls, use_proxies, delay, desired_successes, concurrent_threads = get_user_input()
        targets = [Target(url, i + 1) for i, url in enumerate(urls)]
        
        active_targets = []
        for target in targets:
            console.print(f"\n[yellow]Analisando Alvo #{target.id}: {target.url[:50]}...[/yellow]")
            if target.analyze():
                active_targets.append(target)
                get_custom_answers(target) 
            else:
                console.print(f"[red]Falha ao analisar Alvo #{target.id}. Status: {target.status}[/red]")
        
        if not active_targets:
            console.print("[bold red]\nNenhum alvo válido para processar. Reiniciando...[/bold red]")
            time.sleep(3)
            continue
            
        layout = make_layout()
        banner = pyfiglet.figlet_format("Cortex Tools", font="slant")
        layout["header"].update(Panel(Text(banner, justify="center", style="bold cyan"), border_style="blue", title="[bold white]Google Forms Spammer[/]", subtitle="[cyan]v10.0 - Custom Answers[/]"))
        
        with Live(layout, screen=True, redirect_stderr=False, vertical_overflow="visible") as live:
            proxy_list = []
            if use_proxies:
                good_proxy_logs, bad_proxy_logs = [], deque(maxlen=10)
                total_bad_proxies = [0]
                progress_proxies, q, _ = setup_proxy_test(good_proxy_logs, bad_proxy_logs, total_bad_proxies)
                if progress_proxies:
                    layout["content"].update(Panel(progress_proxies, title="[bold yellow]Teste de Proxy[/]", border_style="yellow"))
                    while q.unfinished_tasks > 0:
                        good_text = Text("\n".join(good_proxy_logs[-10:]))
                        bad_text = Text("\n".join(bad_proxy_logs))
                        layout["side"].update(Panel(good_text, title=f"[green]Aprovados ({len(good_proxy_logs)})[/green]", border_style="green"))
                        layout["footer"].update(Panel(bad_text, title=f"[red]Reprovados ({total_bad_proxies[0]})[/red]", border_style="red"))
                        time.sleep(0.1)
                    proxy_list = good_proxy_logs
                if not proxy_list:
                    layout["footer"].update(Panel(Text("Nenhum proxy funcional. Usando seu IP.", justify="center", style="bold red")))
                    time.sleep(2)

            progress = Progress(TextColumn("[bold blue]{task.description}"), BarColumn(bar_width=None), "[progress.percentage]{task.percentage:>3.1f}%", "•", TextColumn("[green]Sucesso: {task.completed}/{task.total}"), "•", TextColumn("[red]Falhas: {task.fields[f]}"))
            for target in active_targets:
                target.progress_task_id = progress.add_task(f"[Alvo {target.id}] {target.url[:25]}...", total=desired_successes, f=0)
            layout["content"].update(Panel(progress, title="[bold yellow]Progresso do Envio[/]", border_style="yellow"))

            threads = []
            while any(not t.is_complete(desired_successes) for t in active_targets):
                for target in active_targets:
                    if target.is_complete(desired_successes):
                        if not target.status.startswith("Erro"): target.status = "Concluído"
                    elif target.status == "Pronto para Envio": target.status = "Enviando..."
                    if target.is_complete(desired_successes): continue
                    threads_per_target = max(1, concurrent_threads // len(active_targets) if active_targets else 1)
                    current_target_threads = sum(1 for t in threads if t.is_alive() and getattr(t, 'target_id', None) == target.id)
                    if current_target_threads < threads_per_target:
                        t = threading.Thread(target=do_request, args=(target, delay, proxy_list))
                        setattr(t, 'target_id', target.id); threads.append(t); t.start()

                for target in active_targets: progress.update(target.progress_task_id, completed=target.successful_requests, f=target.failed_requests)
                
                side_panel_markup = ""
                for target in targets:
                    status_color = "green" if target.status == "Concluído" else "yellow" if target.status == "Enviando..." else "red" if "Erro" in target.status else "default"
                    side_panel_markup += f"[bold][Alvo {target.id}] {target.url[:35]}...[/bold]\n"
                    side_panel_markup += f"  Status: [{status_color}]{target.status}[/{status_color}]\n"
                    if not target.status.startswith("Erro"): side_panel_markup += f"  Sucesso: {target.successful_requests}/{desired_successes} | Falhas: {target.failed_requests}\n"
                    side_panel_markup += "\n"
                layout["side"].update(Panel(Text.from_markup(side_panel_markup), title="[bold yellow]Status dos Alvos[/]", border_style="yellow"))
                
                log_markup = "\n".join(live_logs)
                layout["footer"].update(Panel(Text.from_markup(log_markup), title="[bold yellow]Logs em Tempo Real[/]", border_style="yellow"))
                threads = [t for t in threads if t.is_alive()]
                time.sleep(0.1)
            
            final_side_markup = ""
            for target in targets:
                status_color = "green" if target.status == "Concluído" else "yellow" if target.status == "Enviando..." else "red" if "Erro" in target.status else "default"
                final_side_markup += f"[bold][Alvo {target.id}] {target.url[:35]}...[/bold]\n"
                final_side_markup += f"  Status: [{status_color}]{target.status}[/{status_color}]\n"
                if not target.status.startswith("Erro"): final_side_markup += f"  Sucesso: {target.successful_requests}/{desired_successes} | Falhas: {target.failed_requests}\n"
                final_side_markup += "\n"
            layout["side"].update(Panel(Text.from_markup(final_side_markup), title="[bold yellow]Status dos Alvos[/]", border_style="yellow"))

            live.console.log("Processo Concluído!")
            time.sleep(2)

        if console.input(f"\n[{ConsoleColor.HEADER}]Deseja rodar novamente? (s/n):[/] ").lower() != 's': break

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: print("\nSaindo...")