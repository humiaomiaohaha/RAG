import json
import random

def generate_medical_data():
    medical_docs = []
    
    psoriasis_docs = [
        {
            "doc_id": "PMID_3312",
            "text": "银屑病治疗中IL-23抑制剂的安全性与有效性研究。本研究对120例中重度银屑病患者进行为期24周的随机对照试验，结果显示IL-23抑制剂在改善PASI评分方面显著优于安慰剂组，安全性良好，主要不良反应为注射部位反应和上呼吸道感染。",
            "source": "《中华皮肤科杂志》2024"
        },
        {
            "doc_id": "PMID_3313", 
            "text": "生物制剂在银屑病治疗中的应用进展。TNF-α抑制剂、IL-17抑制剂和IL-23抑制剂是目前主要的生物制剂类别。阿达木单抗、司库奇尤单抗和古塞奇尤单抗等药物在临床实践中显示出良好的疗效和安全性。",
            "source": "《临床皮肤科杂志》2024"
        },
        {
            "doc_id": "PMID_3314",
            "text": "银屑病生物制剂的长期安全性评估。对500例使用生物制剂治疗银屑病的患者进行为期5年的随访研究，结果显示严重感染、恶性肿瘤和心血管事件的发生率与普通人群相当，证实了生物制剂的长期安全性。",
            "source": "《皮肤病与性病学》2024"
        }
    ]
    
    eczema_docs = [
        {
            "doc_id": "PMID_3315",
            "text": "特应性皮炎的外用治疗策略。钙调神经酶抑制剂和糖皮质激素是主要的外用药物，新型的JAK抑制剂如托法替尼外用制剂在临床试验中显示出良好的疗效，为特应性皮炎患者提供了新的治疗选择。",
            "source": "《中华皮肤科杂志》2024"
        },
        {
            "doc_id": "PMID_3316",
            "text": "特应性皮炎的生物制剂治疗。度普利尤单抗作为首个获批用于特应性皮炎的生物制剂，通过靶向IL-4和IL-13信号通路，显著改善患者的瘙痒症状和皮损严重程度。",
            "source": "《临床皮肤科杂志》2024"
        }
    ]
    
    acne_docs = [
        {
            "doc_id": "PMID_3317",
            "text": "痤疮的药物治疗进展。维A酸类药物、抗生素和抗雄激素药物是痤疮治疗的主要药物。新型的螺内酯和口服避孕药在女性痤疮治疗中显示出良好的效果。",
            "source": "《皮肤病与性病学》2024"
        },
        {
            "doc_id": "PMID_3318",
            "text": "痤疮的外用治疗新策略。过氧化苯甲酰、维A酸和抗生素的外用制剂是痤疮治疗的基础。新型的维A酸受体激动剂和抗炎药物为痤疮治疗提供了新的选择。",
            "source": "《中华皮肤科杂志》2024"
        }
    ]
    
    vitiligo_docs = [
        {
            "doc_id": "PMID_3319",
            "text": "白癜风的治疗进展。糖皮质激素、钙调神经酶抑制剂和光疗是白癜风的主要治疗方法。新型的JAK抑制剂如托法替尼在白癜风治疗中显示出良好的前景。",
            "source": "《临床皮肤科杂志》2024"
        },
        {
            "doc_id": "PMID_3320",
            "text": "白癜风的手术治疗。自体黑素细胞移植和微移植技术在白癜风治疗中显示出良好的效果，特别适用于稳定期白癜风患者的治疗。",
            "source": "《皮肤病与性病学》2024"
        }
    ]
    
    medical_docs.extend(psoriasis_docs)
    medical_docs.extend(eczema_docs)
    medical_docs.extend(acne_docs)
    medical_docs.extend(vitiligo_docs)
    
    with open('medical_docs.json', 'w', encoding='utf-8') as f:
        json.dump(medical_docs, f, ensure_ascii=False, indent=2)
    
    print(f"已生成 {len(medical_docs)} 篇医疗文献数据")
    return medical_docs

if __name__ == "__main__":
    generate_medical_data() 