"""Janela de Gerenciamento de Cargas integrada ao gerador Windows Tkinter."""
from __future__ import annotations
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import catalogo_cargas as catalogo

FIELDS = (
    ("id", "ID (ex.: acucar_ensacado)"),
    ("nome", "Nome exibido no jogo"),
    ("descricao", "Justificativa economica / descricao"),
    ("categoria", "Categoria economica"),
    ("subcategoria", "Subcategoria (opcional)"),
    ("aliases", "Aliases PT/EN (virgula)"),
    ("out_roles", "Setores fornecedores OUT (virgula)"),
    ("in_roles", "Setores compradores IN (virgula)"),
    ("out_companies", "Empresas OUT aprovadas (IDs)"),
    ("in_companies", "Empresas IN aprovadas (IDs)"),
    ("forbidden_roles", "Setores proibidos"),
)
LIST_FIELDS = {"aliases","out_roles","in_roles","out_companies","in_companies","forbidden_roles"}


def abrir_gerenciamento(parent, original_manifest):
    reserved = {catalogo.cargo_id(k) for k in original_manifest}
    top = tk.Toplevel(parent)
    top.title("ETS2 — Gerenciamento de Cargas")
    top.geometry("1020x640")
    top.minsize(800,480)
    top.transient(parent)
    frame = ttk.Frame(top,padding=12)
    frame.pack(fill="both",expand=True)
    ttk.Label(frame,text="Gerenciamento de Cargas",font=("Segoe UI",16,"bold")).pack(anchor="w")
    ttk.Label(frame,text=("As 23 cargas originais sao somente leitura. "
        "Novas cargas exigem cargo_data SII, body_types e regras IN/OUT justificadas."),
        wraplength=920).pack(anchor="w",pady=(0,9))
    cols=("id","nome","categoria","origem","body")
    table=ttk.Treeview(frame,columns=cols,show="headings",selectmode="browse")
    for col,width in (("id",145),("nome",205),("categoria",145),("origem",115),("body",270)):
        table.heading(col,text={"id":"ID","nome":"Mercadoria","categoria":"Categoria",
                                "origem":"Tipo","body":"Body types verificados"}[col])
        table.column(col,width=width,stretch=True)
    table.pack(fill="both",expand=True)
    info=tk.StringVar()
    ttk.Label(frame,textvariable=info).pack(anchor="w",pady=5)
    actions=ttk.Frame(frame)
    actions.pack(fill="x")
    state={"catalog":{}}
    def reload():
        try:
            state["catalog"]=catalogo.load(reserved=reserved)
        except Exception as exc:
            messagebox.showerror("Catalogo invalido",str(exc),parent=top)
            return
        for item in table.get_children():
            table.delete(item)
        for n,(cat,nome) in original_manifest.items():
            cid=catalogo.cargo_id(n)
            table.insert("", "end", iid=cid,values=(cid,nome,cat,"Original","Conforme MOD/DEF importados"))
        for cid,spec in sorted(state["catalog"].items(),key=lambda kv:catalogo.sort_key(kv[0])):
            table.insert("","end",iid=cid,values=(cid,spec["nome"],spec["categoria"],
                         "Adicionada",", ".join(spec["body_types"])))
        info.set(str(len(original_manifest))+" originais + "+
                 str(len(state["catalog"]))+" adicionais = "+
                 str(len(original_manifest)+len(state["catalog"]))+" cadastradas")

    def selection():
        chosen=table.selection()
        if not chosen:
            messagebox.showwarning("Selecione uma carga","Selecione um registro.",parent=top)
            return None
        return chosen[0]

    def open_editor(cid=None):
        source=state["catalog"].get(cid,{}) if cid else {}
        if cid and cid not in state["catalog"]:
            messagebox.showinfo("Carga original","As 23 cargas originais nao podem ser editadas.",parent=top)
            return
        win=tk.Toplevel(top)
        win.title("Editar carga" if cid else "Adicionar carga")
        win.geometry("825x685")
        win.minsize(720,530)
        win.transient(top)
        host=ttk.Frame(win,padding=12);host.pack(fill="both",expand=True)
        canvas=tk.Canvas(host,highlightthickness=0)
        scroll=ttk.Scrollbar(host,orient="vertical",command=canvas.yview)
        canvas.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right",fill="y")
        canvas.pack(side="left",fill="both",expand=True)
        body=ttk.Frame(canvas,padding=4)
        win_id=canvas.create_window((0,0),window=body,anchor="nw")
        body.bind("<Configure>",lambda _e:canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",lambda e:canvas.itemconfigure(win_id,width=e.width))
        values={}
        for key,label in FIELDS:
            line=ttk.Frame(body);line.pack(fill="x",pady=4)
            ttk.Label(line,text=label,width=36).pack(side="left")
            value=source.get(key,[] if key in LIST_FIELDS else "")
            var=tk.StringVar(value=", ".join(value) if isinstance(value,list) else str(value))
            values[key]=var
            entry=ttk.Entry(line,textvariable=var)
            entry.pack(side="left",fill="x",expand=True)
            if cid and key=="id":entry.configure(state="disabled")
        options=ttk.Frame(body);options.pack(fill="x",pady=7)
        evidence={}
        for key,title in (("out_evidence","Exigencia documental OUT"),
                          ("in_evidence","Exigencia documental IN")):
            var=tk.BooleanVar(value=source.get(key,"setor")=="documental")
            evidence[key]=var
            ttk.Checkbutton(options,text=title,variable=var).pack(side="left",padx=8)
        imported=[dict(source)]
        file_info=tk.StringVar(value=(
            "Definicao: "+str(source.get("arquivo_origem","nao importada"))+
            " | body_types: "+", ".join(source.get("body_types",[]))))
        def choose_file():
            new_id=values["id"].get().strip().lower()
            if not catalogo.ID_RE.fullmatch(new_id):
                messagebox.showerror("ID invalido","Preencha um ID valido antes de importar.",parent=win)
                return
            p=filedialog.askopenfilename(parent=win,title="Importar cargo_data original",
                                         filetypes=[("SII/SUI","*.sii *.sui"),("Todos","*.*")])
            if not p:return
            try:
                imported[0].update(catalogo.import_definition(p,new_id))
                file_info.set("Definicao importada: "+p+" | body_types: "+
                              ", ".join(imported[0]["body_types"]))
            except Exception as exc:
                messagebox.showerror("Importacao bloqueada",str(exc),parent=win)
        ttk.Button(body,text="Importar arquivo SII / SUI original",command=choose_file).pack(fill="x",pady=4)
        ttk.Label(body,textvariable=file_info,wraplength=720).pack(anchor="w",pady=(2,8))
        ttk.Label(body,text=("OUT = quem fornece, IN = quem compra. Setor so e autorizado "
            "se a identidade da empresa for reconhecida com alta confianca. "
            "Marque exigencia documental quando precisar confirmar a mercadoria no IN/OUT original."),
            wraplength=720).pack(anchor="w",pady=6)
        def save_item():
            try:
                payload=dict(imported[0])
                for key,var in values.items():
                    payload[key]=([x.strip().lower() for x in var.get().split(",") if x.strip()]
                                  if key in LIST_FIELDS else var.get().strip())
                for key,var in evidence.items():
                    payload[key]="documental" if var.get() else "setor"
                if cid and payload["id"]!=cid:
                    raise ValueError("O ID de uma carga cadastrada nao pode ser alterado")
                checked=catalogo.validate(payload,reserved=reserved)
                updated=dict(state["catalog"])
                updated[checked["id"]]=checked
                catalogo.save(updated,reserved=reserved)
                reload();win.destroy()
            except Exception as exc:
                messagebox.showerror("Cadastro bloqueado",str(exc),parent=win)
        ttk.Button(body,text="SALVAR CARGA VALIDADA",command=save_item).pack(fill="x",pady=(8,20))
        win.grab_set()
    def edit_selected():
        cid=selection()
        if cid:open_editor(cid)
    def remove_selected():
        cid=selection()
        if cid is None:return
        if cid not in state["catalog"]:
            messagebox.showinfo("Original protegida","Nao pode remover mercadorias originais.",parent=top)
            return
        if not messagebox.askyesno("Remover cadastro",
            "Excluir "+cid+" do catalogo?\nO SCS anterior NAO sera alterado, mas "
            "referencias antigas exigirao revisao na proxima auditoria.",parent=top):
            return
        remaining=dict(state["catalog"]);del remaining[cid]
        try:
            catalogo.save(remaining,reserved=reserved)
            reload()
        except Exception as exc:
            messagebox.showerror("Remocao falhou",str(exc),parent=top)
    ttk.Button(actions,text="Adicionar nova carga",command=open_editor).pack(side="left",padx=4)
    ttk.Button(actions,text="Editar selecionada",command=edit_selected).pack(side="left",padx=4)
    ttk.Button(actions,text="Remover adicional",command=remove_selected).pack(side="left",padx=4)
    ttk.Button(actions,text="Atualizar lista",command=reload).pack(side="left",padx=4)
    ttk.Button(actions,text="Fechar",command=top.destroy).pack(side="right",padx=4)
    table.bind("<Double-1>",lambda _e:edit_selected())
    reload()
